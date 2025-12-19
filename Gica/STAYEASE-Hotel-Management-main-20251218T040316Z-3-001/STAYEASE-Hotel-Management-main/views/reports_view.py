from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton,
                             QMessageBox, QHBoxLayout, QComboBox, QDateEdit,
                             QFrame, QProgressDialog, QApplication)
from PyQt6.QtCore import Qt, QDate, QThread, pyqtSignal
from PyQt6.QtGui import QFont
import csv
from datetime import datetime, timedelta, date
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend to avoid threading warnings
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import io
from models.reservation_model import ReservationModel
import tempfile
import os
import sys
import subprocess


class PDFExportThread(QThread):
    """Thread for PDF export to prevent UI freezing"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, reservations, charts_data, report_title):
        super().__init__()
        self.reservations = reservations
        self.charts_data = charts_data
        self.report_title = report_title

    def run(self):
        try:
            # Try to import reportlab
            try:
                from reportlab.pdfgen import canvas
                from reportlab.lib.pagesizes import letter, A4
                from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.lib import colors
                from reportlab.lib.units import inch
                from reportlab.lib.enums import TA_CENTER
            except ImportError:
                self.error.emit(
                    "ReportLab module is required for PDF export.\nPlease install it using: pip install reportlab")
                return

            # Create reports directory if it doesn't exist
            os.makedirs('reports', exist_ok=True)
            
            # Create filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"reports/hotel_report_{timestamp}.pdf"

            # Create directory if it doesn't exist
            os.makedirs("reports", exist_ok=True)

            # Create PDF document
            doc = SimpleDocTemplate(
                filename,
                pagesize=A4,
                rightMargin=30,
                leftMargin=30,
                topMargin=30,
                bottomMargin=30
            )

            self.progress.emit(10)

            # Create story (content)
            story = []
            styles = getSampleStyleSheet()

            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#2c3e50')
            )

            subtitle_style = ParagraphStyle(
                'CustomSubtitle',
                parent=styles['Heading2'],
                fontSize=16,
                spaceAfter=20,
                textColor=colors.HexColor('#3498db')
            )

            # Title
            story.append(Paragraph(self.report_title, title_style))
            story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                                   ParagraphStyle('DateStyle', parent=styles['Normal'], alignment=TA_CENTER)))
            story.append(Spacer(1, 20))

            self.progress.emit(20)

            # Summary Section
            story.append(Paragraph("Executive Summary", subtitle_style))

            # Calculate summary statistics
            total_reservations = len(self.reservations)
            total_revenue = sum(float(res.get('total_price', 0)) for res in self.reservations)
            avg_revenue = total_revenue / total_reservations if total_reservations > 0 else 0

            # Status counts
            status_counts = {}
            for res in self.reservations:
                status = res.get('status', 'Unknown')
                status_counts[status] = status_counts.get(status, 0) + 1

            # Create summary table
            summary_data = [
                ["Metric", "Value"],
                ["Total Reservations", str(total_reservations)],
                ["Total Revenue", f"₱{total_revenue:,.2f}"],
                ["Average Revenue per Booking", f"₱{avg_revenue:,.2f}"],
                ["Report Period", self.charts_data.get('period', 'Custom Range')]
            ]

            # Add status counts to summary
            for status, count in status_counts.items():
                summary_data.append([f"{status} Bookings", str(count)])

            summary_table = Table(summary_data, colWidths=[2.5 * inch, 2 * inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
            ]))

            story.append(summary_table)
            story.append(Spacer(1, 30))

            self.progress.emit(40)

            # Charts Section
            story.append(Paragraph("Analytics Charts", subtitle_style))
            story.append(Spacer(1, 10))

            # Save charts as temporary images
            chart_filenames = []

            # Create and save each chart
            for i, chart_func in enumerate([
                self._create_revenue_chart,
                self._create_status_chart,
                self._create_room_chart,
                self._create_daily_chart
            ]):
                try:
                    img_data = chart_func(self.reservations)
                    if img_data:
                        # Save to temporary file
                        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
                        temp_file.write(img_data.getvalue())
                        temp_file.close()
                        chart_filenames.append(temp_file.name)

                        # Add to PDF
                        story.append(Image(temp_file.name, width=6 * inch, height=4 * inch))
                        story.append(Spacer(1, 10))

                        self.progress.emit(40 + (i + 1) * 10)
                except Exception as e:
                    print(f"Error creating chart {i}: {e}")

            self.progress.emit(80)

            # Detailed Data Section
            story.append(Paragraph("Detailed Reservation Data", subtitle_style))

            # Prepare data for table
            table_data = [["ID", "Customer", "Room", "Check-In", "Check-Out", "Status", "Price"]]

            # Limit to first 50 reservations for PDF readability
            for res in self.reservations[:50]:
                table_data.append([
                    str(res.get('id', '')),
                    res.get('customer_name', ''),
                    res.get('room_number', ''),
                    res.get('check_in', ''),
                    res.get('check_out', ''),
                    res.get('status', ''),
                    f"₱{float(res.get('total_price', 0)):,.2f}"
                ])

            # If there are more than 50 reservations, add a note
            if len(self.reservations) > 50:
                table_data.append(["", f"... and {len(self.reservations) - 50} more reservations", "", "", "", "", ""])

            # Create table
            detailed_table = Table(table_data,
                                   colWidths=[0.5 * inch, 1.5 * inch, 0.8 * inch, 1 * inch, 1 * inch, 1 * inch,
                                              1 * inch])
            detailed_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
            ]))

            story.append(detailed_table)
            story.append(Spacer(1, 20))

            # Footer note
            footer_text = "This report was generated by Hotel Management System. All data is confidential."
            story.append(Paragraph(footer_text,
                                   ParagraphStyle('Footer', parent=styles['Normal'],
                                                  fontSize=8, alignment=TA_CENTER,
                                                  textColor=colors.grey)))

            self.progress.emit(90)

            # Build PDF
            doc.build(story)

            # Clean up temporary files
            for temp_file in chart_filenames:
                try:
                    os.unlink(temp_file)
                except:
                    pass

            self.progress.emit(100)
            self.finished.emit(filename)

        except Exception as e:
            self.error.emit(f"Error creating PDF: {str(e)}")

    def _create_revenue_chart(self, reservations):
        """Create revenue trend chart image"""
        fig, ax = plt.subplots(figsize=(8, 5))

        # Group by date
        revenue_by_date = {}
        for res in reservations:
            try:
                date_val = res['check_in']
                if isinstance(date_val, str):
                    d_obj = datetime.strptime(date_val, '%Y-%m-%d')
                else:
                    d_obj = date_val
                
                revenue = float(res.get('total_price', 0))
                date_str = d_obj.strftime('%m-%d')
                revenue_by_date[date_str] = revenue_by_date.get(date_str, 0) + revenue
            except Exception as e:
                print(f"Error in _create_revenue_chart: {e}")
                continue

        if revenue_by_date:
            dates = sorted(revenue_by_date.keys())
            revenues = [revenue_by_date[d] for d in dates]

            ax.plot(dates, revenues, marker='o', linewidth=2, color='#3498db', markersize=6)
            ax.fill_between(dates, revenues, alpha=0.3, color='#3498db')
            ax.set_xlabel('Date')
            ax.set_ylabel('Revenue (₱)')
            ax.set_title('Revenue Trend', fontweight='bold')
            ax.grid(True, alpha=0.3)
            ax.tick_params(axis='x', rotation=45)

        plt.tight_layout()

        # Save to bytes buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return buf

    def _create_status_chart(self, reservations):
        """Create status distribution chart image"""
        fig, ax = plt.subplots(figsize=(8, 5))

        status_counts = {}
        for res in reservations:
            status = res.get('status', 'Unknown')
            status_counts[status] = status_counts.get(status, 0) + 1

        if status_counts:
            labels = list(status_counts.keys())
            sizes = list(status_counts.values())

            color_map = {
                'Confirmed': '#2ecc71',
                'Pending': '#f39c12',
                'Cancelled': '#e74c3c',
                'Checked-in': '#3498db',
                'Checked-out': '#9b59b6'
            }
            colors = [color_map.get(label, '#95a5a6') for label in labels]

            ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            ax.set_title('Reservation Status Distribution', fontweight='bold')
            ax.axis('equal')

        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return buf

    def _create_room_chart(self, reservations):
        """Create room distribution chart image"""
        fig, ax = plt.subplots(figsize=(8, 5))

        room_counts = {}
        for res in reservations:
            room = res.get('room_number', 'Unknown')
            room_counts[room] = room_counts.get(room, 0) + 1

        if room_counts:
            # Get top 10 rooms
            sorted_rooms = sorted(room_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            rooms = [r[0] for r in sorted_rooms]
            counts = [r[1] for r in sorted_rooms]

            bars = ax.bar(rooms, counts, color='#9b59b6', alpha=0.8)
            ax.set_xlabel('Room Number')
            ax.set_ylabel('Number of Reservations')
            ax.set_title('Top 10 Most Booked Rooms', fontweight='bold')
            ax.tick_params(axis='x', rotation=45)
            ax.grid(True, alpha=0.3, axis='y')

            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2., height,
                        f'{int(height)}', ha='center', va='bottom', fontsize=9)

        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return buf

    def _create_daily_chart(self, reservations):
        """Create daily reservations chart image"""
        fig, ax = plt.subplots(figsize=(8, 5))

        daily_counts = {}
        for res in reservations:
            try:
                date_val = res['check_in']
                if isinstance(date_val, str):
                    date_obj = datetime.strptime(date_val, '%Y-%m-%d')
                else:
                    date_obj = date_val
                
                date_str = date_obj.strftime('%m-%d')
                daily_counts[date_str] = daily_counts.get(date_str, 0) + 1
            except:
                continue

        if daily_counts:
            dates = sorted(daily_counts.keys())[-14:]  # Last 14 days
            counts = [daily_counts[d] for d in dates]

            bars = ax.bar(dates, counts, color='#e74c3c', alpha=0.8)
            ax.set_xlabel('Date (MM-DD)')
            ax.set_ylabel('Reservations')
            ax.set_title('Daily Reservation Count (Last 14 days)', fontweight='bold')
            ax.tick_params(axis='x', rotation=45)
            ax.grid(True, alpha=0.3, axis='y')

            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2., height,
                        f'{int(height)}', ha='center', va='bottom', fontsize=8)

        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return buf


class ReportsView(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.reservations = []
        self.init_ui()
        self.load_reservations()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Title
        title = QLabel("📊 Reports & Analytics")
        title.setStyleSheet("font-family: Arial; font-size: 18pt; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        main_layout.addWidget(title)

        # Description
        desc = QLabel("Generate and export reports with visual analytics for reservations and revenue.")
        desc.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        main_layout.addWidget(desc)

        # Filter Controls
        filter_frame = QFrame()
        filter_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(20, 15, 20, 15)
        filter_layout.setSpacing(15)

        # Icon for filter
        filter_icon = QLabel("📅")
        filter_icon.setStyleSheet("font-size: 20px; margin-right: 5px;")
        filter_layout.addWidget(filter_icon)

        # Time period filter
        period_label = QLabel("Time Period:")
        period_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
        filter_layout.addWidget(period_label)

        self.period_combo = QComboBox()
        self.period_combo.addItems(
            ["Last 7 days", "Last 30 days", "Last 90 days", "This month", "Last month", "Custom"])
        self.period_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.period_combo.currentTextChanged.connect(self.update_charts)
        filter_layout.addWidget(self.period_combo)

        # Date range for custom selection
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.start_date.setCalendarPopup(True)
        self.start_date.dateChanged.connect(self.update_charts)
        filter_layout.addWidget(QLabel("From:"))
        filter_layout.addWidget(self.start_date)

        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        self.end_date.dateChanged.connect(self.update_charts)
        filter_layout.addWidget(QLabel("To:"))
        filter_layout.addWidget(self.end_date)

        filter_layout.addStretch()
        main_layout.addWidget(filter_frame)

        # Charts Container
        charts_container = QVBoxLayout()

        # Row 1: Two charts side by side
        row1_layout = QHBoxLayout()

        # Revenue Chart
        revenue_frame = QFrame()
        revenue_frame.setStyleSheet("""
            QFrame {
                background-color: #F5F5F5;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        revenue_layout = QVBoxLayout(revenue_frame)
        revenue_title = QLabel("📈 Revenue Trend")
        revenue_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
        revenue_layout.addWidget(revenue_title)

        self.revenue_fig = Figure(figsize=(6, 4), dpi=80)
        self.revenue_canvas = FigureCanvas(self.revenue_fig)
        revenue_layout.addWidget(self.revenue_canvas)
        row1_layout.addWidget(revenue_frame)

        # Reservations Status Chart
        status_frame = QFrame()
        status_frame.setStyleSheet("""
            QFrame {
                background-color: #F5F5F5;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        status_layout = QVBoxLayout(status_frame)
        status_title = QLabel("📊 Reservation Status")
        status_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
        status_layout.addWidget(status_title)

        self.status_fig = Figure(figsize=(6, 4), dpi=80)
        self.status_canvas = FigureCanvas(self.status_fig)
        status_layout.addWidget(self.status_canvas)
        row1_layout.addWidget(status_frame)

        charts_container.addLayout(row1_layout)

        # Row 2: Two more charts
        row2_layout = QHBoxLayout()

        # Room Occupancy Chart
        occupancy_frame = QFrame()
        occupancy_frame.setStyleSheet("""
            QFrame {
                background-color: #F5F5F5;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        occupancy_layout = QVBoxLayout(occupancy_frame)
        occupancy_title = QLabel("🏨 Room Type Distribution")
        occupancy_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
        occupancy_layout.addWidget(occupancy_title)

        self.occupancy_fig = Figure(figsize=(6, 4), dpi=80)
        self.occupancy_canvas = FigureCanvas(self.occupancy_fig)
        occupancy_layout.addWidget(self.occupancy_canvas)
        row2_layout.addWidget(occupancy_frame)

        # Daily Reservations Chart
        daily_frame = QFrame()
        daily_frame.setStyleSheet("""
            QFrame {
                background-color: #F5F5F5;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        daily_layout = QVBoxLayout(daily_frame)
        daily_title = QLabel("📅 Daily Reservations")
        daily_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
        daily_layout.addWidget(daily_title)

        self.daily_fig = Figure(figsize=(6, 4), dpi=80)
        self.daily_canvas = FigureCanvas(self.daily_fig)
        daily_layout.addWidget(self.daily_canvas)
        row2_layout.addWidget(daily_frame)

        charts_container.addLayout(row2_layout)
        main_layout.addLayout(charts_container)

        # Export Buttons
        export_frame = QFrame()
        export_layout = QHBoxLayout(export_frame)

        export_csv_btn = QPushButton("📊 Export to CSV")
        export_csv_btn.setFixedSize(200, 40)
        export_csv_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        export_csv_btn.clicked.connect(self.export_csv)
        export_layout.addWidget(export_csv_btn)

        self.export_pdf_btn = QPushButton("📄 Export Full Report (PDF)")
        self.export_pdf_btn.setFixedSize(200, 40)
        self.export_pdf_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        self.export_pdf_btn.clicked.connect(self.export_pdf)
        export_layout.addWidget(self.export_pdf_btn)

        # Export Chart button removed as requested


        export_layout.addStretch()
        main_layout.addWidget(export_frame)

        self.setLayout(main_layout)

    def load_reservations(self):
        """Load reservations from the model"""
        try:
            self.reservations = ReservationModel.get_all_reservations()
            self.update_charts()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load reservations: {str(e)}")

    def get_filtered_reservations(self):
        """Get reservations filtered by selected time period"""
        if not self.reservations:
            return []

        period = self.period_combo.currentText()
        end_date = datetime.now()

        if period == "Last 7 days":
            start_date = end_date - timedelta(days=7)
        elif period == "Last 30 days":
            start_date = end_date - timedelta(days=30)
        elif period == "Last 90 days":
            start_date = end_date - timedelta(days=90)
        elif period == "This month":
            start_date = end_date.replace(day=1)
        elif period == "Last month":
            start_date = (end_date.replace(day=1) - timedelta(days=1)).replace(day=1)
            end_date = end_date.replace(day=1) - timedelta(days=1)
        else:  # Custom
            start_date = self.start_date.date().toPyDate()
            end_date = self.end_date.date().toPyDate()

        filtered = []
        for res in self.reservations:
            try:
                check_in = res['check_in']
                if isinstance(check_in, str):
                    check_in = datetime.strptime(check_in, '%Y-%m-%d')
                elif isinstance(check_in, date) and not isinstance(check_in, datetime):
                    # Convert date to datetime for comparison
                    check_in = datetime.combine(check_in, datetime.min.time())
                
                # Ensure start_date and end_date are datetime objects for comparison
                start_dt = datetime.combine(start_date if isinstance(start_date, date) else start_date.date(), datetime.min.time()) if not isinstance(start_date, datetime) else start_date
                end_dt = datetime.combine(end_date if isinstance(end_date, date) else end_date.date(), datetime.max.time()) if not isinstance(end_date, datetime) else end_date.replace(hour=23, minute=59, second=59)

                if start_dt <= check_in <= end_dt:
                    filtered.append(res)
            except Exception as e:
                print(f"Error filtering reservation: {e}")
                continue

        return filtered

    def update_charts(self):
        """Update all charts with filtered data"""
        filtered_reservations = self.get_filtered_reservations()

        # Clear all figures
        self.revenue_fig.clear()
        self.status_fig.clear()
        self.occupancy_fig.clear()
        self.daily_fig.clear()

        if not filtered_reservations:
            # Show empty state
            self.show_empty_charts()
        else:
            # Plot revenue trend
            self.plot_revenue_trend(filtered_reservations)

            # Plot reservation status
            self.plot_reservation_status(filtered_reservations)

            # Plot room type distribution
            self.plot_room_type_distribution(filtered_reservations)

            # Plot daily reservations
            self.plot_daily_reservations(filtered_reservations)

        # Refresh canvases
        self.revenue_canvas.draw()
        self.status_canvas.draw()
        self.occupancy_canvas.draw()
        self.daily_canvas.draw()

    def show_empty_charts(self):
        """Display empty state for charts"""
        for fig, title in [(self.revenue_fig, "Revenue Trend"),
                           (self.status_fig, "Reservation Status"),
                           (self.occupancy_fig, "Room Type Distribution"),
                           (self.daily_fig, "Daily Reservations")]:
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, 'No data available\nfor selected period',
                    horizontalalignment='center',
                    verticalalignment='center',
                    transform=ax.transAxes,
                    fontsize=12,
                    color='gray')
            ax.set_facecolor('#f8f9fa')
            ax.set_facecolor('#f8f9fa')
            # ax.set_title(title, fontsize=12, fontweight='bold') # Duplicate title removed
            ax.axis('off')

    def plot_revenue_trend(self, reservations):
        """Plot revenue trend over time"""
        ax = self.revenue_fig.add_subplot(111)

        # Group by date
        revenue_by_date = {}
        for res in reservations:
            try:
                date_val = res['check_in']
                if isinstance(date_val, str):
                    d_obj = datetime.strptime(date_val, '%Y-%m-%d')
                else:
                    d_obj = date_val
                
                revenue = float(res.get('total_price', 0))
                date_str = d_obj.strftime('%Y-%m-%d')
                revenue_by_date[date_str] = revenue_by_date.get(date_str, 0) + revenue
            except Exception as e:
                print(f"Error in plot_revenue_trend: {e}")
                continue

        if not revenue_by_date:
            return

        # Sort by date
        dates = sorted(revenue_by_date.keys())
        revenues = [revenue_by_date[d] for d in dates]

        # Plot
        ax.plot(dates, revenues, marker='o', linewidth=2, color='#3498db', markersize=6)
        ax.fill_between(dates, revenues, alpha=0.3, color='#3498db')
        ax.set_xlabel('Date', fontsize=10)
        ax.set_ylabel('Revenue (₱)', fontsize=10)
        # ax.set_title('Revenue Trend', fontsize=12, fontweight='bold') # Duplicate title removed
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='x', rotation=45)
        ax.set_facecolor('#f8f9fa')
        try:
             self.revenue_fig.tight_layout()
        except UserWarning:
             pass

    def plot_reservation_status(self, reservations):
        """Plot pie chart of reservation status"""
        ax = self.status_fig.add_subplot(111)

        status_counts = {}
        for res in reservations:
            status = res.get('status', 'Unknown')
            status_counts[status] = status_counts.get(status, 0) + 1

        if not status_counts:
            return

        labels = list(status_counts.keys())
        sizes = list(status_counts.values())

        # Colors based on status
        color_map = {
            'Confirmed': '#2ecc71',
            'Pending': '#f39c12',
            'Cancelled': '#e74c3c',
            'Checked-in': '#3498db',
            'Checked-out': '#9b59b6'
        }
        colors = [color_map.get(label, '#95a5a6') for label in labels]

        # Plot pie chart
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors,
                                          autopct='%1.1f%%', startangle=90)

        # Style the text
        for text in texts:
            text.set_fontsize(9)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(8)

            autotext.set_fontsize(8)
        
        # ax.set_title('Reservation Status Distribution', fontsize=12, fontweight='bold') # Duplicate title removed
        ax.axis('equal')

    def plot_room_type_distribution(self, reservations):
        """Plot bar chart of room type distribution"""
        ax = self.occupancy_fig.add_subplot(111)

        room_counts = {}
        for res in reservations:
            room = res.get('room_number', 'Unknown')
            room_counts[room] = room_counts.get(room, 0) + 1

        if not room_counts:
            return

        rooms = list(room_counts.keys())
        counts = list(room_counts.values())

        # Sort by count
        sorted_data = sorted(zip(rooms, counts), key=lambda x: x[1], reverse=True)
        rooms, counts = zip(*sorted_data) if sorted_data else ([], [])

        # Create bar chart
        bars = ax.bar(rooms, counts, color='#9b59b6', alpha=0.8)

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height,
                    f'{int(height)}', ha='center', va='bottom', fontsize=9)

        ax.set_xlabel('Room Number', fontsize=10)
        ax.set_ylabel('Reservations', fontsize=10)
        # ax.set_title('Most Booked Rooms', fontsize=12, fontweight='bold') # Duplicate title removed
        ax.grid(True, alpha=0.3, axis='y')
        ax.set_facecolor('#f8f9fa')
        ax.tick_params(axis='x', rotation=45)
        self.occupancy_fig.tight_layout()

    def plot_daily_reservations(self, reservations):
        """Plot daily reservations count"""
        # Create subplot AFTER checking data to avoid empty axes
        
        # Group by date
        daily_counts = {}
        for res in reservations:
            try:
                date_val = res['check_in']
                if isinstance(date_val, str):
                    d_obj = datetime.strptime(date_val, '%Y-%m-%d')
                else:
                    d_obj = date_val
                
                date_str = d_obj.strftime('%m-%d')
                daily_counts[date_str] = daily_counts.get(date_str, 0) + 1
            except Exception as e:
                print(f"Error in plot_daily_reservations: {e}")
                continue

        ax = self.daily_fig.add_subplot(111)
        
        if not daily_counts:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center', transform=ax.transAxes, color='gray')
            ax.axis('off')
            return

        # Sort by date
        dates = sorted(daily_counts.keys())
        counts = [daily_counts[d] for d in dates]

        # Plot bar chart
        bars = ax.bar(dates, counts, color='#e74c3c', alpha=0.8)

        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height,
                    f'{int(height)}', ha='center', va='bottom', fontsize=8)

        ax.set_xlabel('Date (MM-DD)', fontsize=10)
        ax.set_ylabel('Number of Reservations', fontsize=10)
        ax.set_xlabel('Date (MM-DD)', fontsize=10)
        ax.set_ylabel('Number of Reservations', fontsize=10)
        # ax.set_title('Daily Reservation Count', fontsize=12, fontweight='bold') # Duplicate title removed
        ax.grid(True, alpha=0.3, axis='y')
        ax.set_facecolor('#f8f9fa')
        ax.tick_params(axis='x', rotation=45)
        self.daily_fig.tight_layout()

    def export_csv(self):
        """Export filtered reservations to CSV"""
        try:
            filtered_reservations = self.get_filtered_reservations()
            if not filtered_reservations:
                QMessageBox.warning(self, "No Data", "No reservation data available for the selected period.")
                return

            # Create reports directory if it doesn't exist
            os.makedirs("reports", exist_ok=True)

            filename = f"reports/reservations_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Customer", "Room", "Check In", "Check Out", "Status", "Total Price"])
                for res in filtered_reservations:
                    writer.writerow([
                        res['id'],
                        res['customer_name'],
                        res['room_number'],
                        res['check_in'],
                        res['check_out'],
                        res['status'],
                        res['total_price']
                    ])

            QMessageBox.information(self, "Success",
                                    f"CSV report exported successfully!\nSaved to: {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export CSV: {str(e)}")

    def export_pdf(self):
        """Export comprehensive PDF report with charts and data"""
        try:
            # Check if reportlab is installed
            try:
                from reportlab.pdfgen import canvas
            except ImportError:
                QMessageBox.information(
                    self,
                    "Install Required Library",
                    "PDF Export requires ReportLab module.\n\n"
                    "Please install it using:\n"
                    "pip install reportlab\n\n"
                    "Or for Anaconda:\n"
                    "conda install -c conda-forge reportlab"
                )
                return

            filtered_reservations = self.get_filtered_reservations()

            if not filtered_reservations:
                QMessageBox.warning(self, "No Data", "No reservation data available for the selected period.")
                return

            # Create report title based on period
            period = self.period_combo.currentText()
            if period == "Custom":
                start_date = self.start_date.date().toString("yyyy-MM-dd")
                end_date = self.end_date.date().toString("yyyy-MM-dd")
                report_title = f"Hotel Management Report - {start_date} to {end_date}"
            else:
                report_title = f"Hotel Management Report - {period}"

            # Prepare charts data
            charts_data = {
                'period': period,
                'reservation_count': len(filtered_reservations)
            }

            # Create and show progress dialog
            self.progress_dialog = QProgressDialog("Generating PDF Report...", "Cancel", 0, 100, self)
            self.progress_dialog.setWindowTitle("Exporting PDF")
            self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
            self.progress_dialog.setMinimumDuration(0)

            # Create export thread
            self.export_thread = PDFExportThread(filtered_reservations, charts_data, report_title)
            self.export_thread.progress.connect(self.progress_dialog.setValue)
            self.export_thread.finished.connect(self.on_pdf_export_finished)
            self.export_thread.error.connect(self.on_pdf_export_error)

            # Connect cancel button
            self.progress_dialog.canceled.connect(self.export_thread.terminate)

            # Start thread
            self.export_thread.start()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start PDF export: {str(e)}")

    def on_pdf_export_finished(self, filename):
        """Handle successful PDF export"""
        self.progress_dialog.close()

        # Show success message with option to open file
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Export Successful")
        msg.setText(f"PDF report has been generated successfully!")
        msg.setInformativeText(f"File saved to:\n{filename}")

        # Add buttons
        open_btn = msg.addButton("Open File", QMessageBox.ButtonRole.AcceptRole)
        open_folder_btn = msg.addButton("Open Folder", QMessageBox.ButtonRole.ActionRole)
        msg.addButton("OK", QMessageBox.ButtonRole.RejectRole)

        msg.exec()

        # Handle button clicks
        if msg.clickedButton() == open_btn:
            self.open_file(filename)
        elif msg.clickedButton() == open_folder_btn:
            self.open_folder(filename)

    def on_pdf_export_error(self, error_message):
        """Handle PDF export errors"""
        self.progress_dialog.close()
        QMessageBox.critical(self, "Export Error", error_message)

    def export_charts_image(self):
        """Export all charts as a single image"""
        try:
            filtered_reservations = self.get_filtered_reservations()

            if not filtered_reservations:
                QMessageBox.warning(self, "No Data", "No reservation data available for the selected period.")
                return

            # Create reports directory if it doesn't exist
            os.makedirs("reports", exist_ok=True)

            filename = f"reports/charts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

            # Create a new figure with all charts
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))

            # Recreate each chart on the new figure
            self._plot_revenue_trend_on_axis(filtered_reservations, axes[0, 0])
            self._plot_reservation_status_on_axis(filtered_reservations, axes[0, 1])
            self._plot_room_type_distribution_on_axis(filtered_reservations, axes[1, 0])
            self._plot_daily_reservations_on_axis(filtered_reservations, axes[1, 1])

            plt.suptitle(f"Hotel Analytics Report - {datetime.now().strftime('%Y-%m-%d')}",
                         fontsize=16, fontweight='bold')
            plt.tight_layout()
            plt.savefig(filename, dpi=150, bbox_inches='tight')
            plt.close(fig)

            QMessageBox.information(self, "Success",
                                    f"Charts exported successfully!\nSaved to: {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export charts: {str(e)}")

    def _plot_revenue_trend_on_axis(self, reservations, ax):
        """Helper method to plot revenue trend on given axis"""
        if not reservations:
            ax.text(0.5, 0.5, 'No data', ha='center', va='center')
            return

        revenue_by_date = {}
        for res in reservations:
            try:
                date = datetime.strptime(res['check_in'], '%Y-%m-%d')
                revenue = float(res.get('total_price', 0))
                date_str = date.strftime('%Y-%m-%d')
                revenue_by_date[date_str] = revenue_by_date.get(date_str, 0) + revenue
            except:
                continue

        dates = sorted(revenue_by_date.keys())
        revenues = [revenue_by_date[d] for d in dates]

        ax.plot(dates, revenues, marker='o', linewidth=2, color='#3498db')
        ax.set_title('Revenue Trend')
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, alpha=0.3)

    def _plot_reservation_status_on_axis(self, reservations, ax):
        """Helper method to plot reservation status on given axis"""
        if not reservations:
            ax.text(0.5, 0.5, 'No data', ha='center', va='center')
            return

        status_counts = {}
        for res in reservations:
            status = res.get('status', 'Unknown')
            status_counts[status] = status_counts.get(status, 0) + 1

        labels = list(status_counts.keys())
        sizes = list(status_counts.values())

        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.set_title('Reservation Status')
        ax.axis('equal')

    def _plot_room_type_distribution_on_axis(self, reservations, ax):
        """Helper method to plot room type distribution on given axis"""
        if not reservations:
            ax.text(0.5, 0.5, 'No data', ha='center', va='center')
            return

        room_counts = {}
        for res in reservations:
            room = res.get('room_number', 'Unknown')
            room_counts[room] = room_counts.get(room, 0) + 1

        rooms = list(room_counts.keys())[:10]  # Top 10 rooms
        counts = [room_counts[r] for r in rooms]

        ax.bar(rooms, counts, color='#9b59b6', alpha=0.8)
        ax.set_title('Top Booked Rooms')
        ax.tick_params(axis='x', rotation=45)

    def _plot_daily_reservations_on_axis(self, reservations, ax):
        """Helper method to plot daily reservations on given axis"""
        if not reservations:
            ax.text(0.5, 0.5, 'No data', ha='center', va='center')
            return

        daily_counts = {}
        for res in reservations:
            try:
                date = datetime.strptime(res['check_in'], '%Y-%m-%d')
                date_str = date.strftime('%m-%d')
                daily_counts[date_str] = daily_counts.get(date_str, 0) + 1
            except:
                continue

        dates = sorted(daily_counts.keys())[-10:]  # Last 10 days
        counts = [daily_counts[d] for d in dates]

        ax.bar(dates, counts, color='#e74c3c', alpha=0.8)
        ax.set_title('Daily Reservations (Last 10 days)')
        ax.tick_params(axis='x', rotation=45)

    def open_file(self, filepath):
        """Open the exported file with default application"""
        try:
            if sys.platform == "win32":
                os.startfile(filepath)
            elif sys.platform == "darwin":  # macOS
                subprocess.run(["open", filepath])
            else:  # Linux
                subprocess.run(["xdg-open", filepath])
        except Exception as e:
            print(f"Error opening file: {e}")

    def open_folder(self, filepath):
        """Open the folder containing the exported file"""
        try:
            folder_path = os.path.dirname(os.path.abspath(filepath))

            if sys.platform == "win32":
                os.startfile(folder_path)
            elif sys.platform == "darwin":  # macOS
                subprocess.run(["open", folder_path])
            else:  # Linux
                subprocess.run(["xdg-open", folder_path])
        except Exception as e:
            print(f"Error opening folder: {e}")
