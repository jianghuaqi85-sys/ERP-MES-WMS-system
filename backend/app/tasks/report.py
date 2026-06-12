import os
from datetime import datetime
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from app.celery_app import celery_app
from app.core.database import SessionLocal
from app.apps.erp.models import SalesOrder

# Register Chinese font to handle Chinese characters in PDF
def register_chinese_font():
    font_paths = [
        r"C:\Windows\Fonts\msyh.ttc",    # Windows Microsoft YaHei
        r"C:\Windows\Fonts\simsun.ttc",   # Windows SimSun
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", # Debian wqy-microhei
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                # Register the font
                pdfmetrics.registerFont(TTFont("ChineseFont", path))
                return "ChineseFont"
            except Exception:
                continue
    return "Helvetica"

@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=10,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True
)
def generate_report(self, order_id: int) -> str:
    """
    Generate a financial report PDF for a SalesOrder and save it to the reports/ directory.
    Returns the file path.
    """
    db: Session = SessionLocal()
    try:
        # Fetch SalesOrder
        order = db.query(SalesOrder).filter(SalesOrder.id == order_id).first()
        if not order:
            raise ValueError(f"Sales order {order_id} not found")
        
        # Ensure reports directory exists
        reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "reports")
        os.makedirs(reports_dir, exist_ok=True)
        
        # Output file path
        # Use task ID to make it unique
        filename = f"financial_report_{order_id}_{self.request.id}.pdf"
        file_path = os.path.join(reports_dir, filename)
        
        # Setup document
        doc = SimpleDocTemplate(
            file_path,
            pagesize=letter,
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=30
        )
        
        font_name = register_chinese_font()
        styles = getSampleStyleSheet()
        
        # Custom Styles
        title_style = ParagraphStyle(
            name="TitleStyle",
            fontName=font_name,
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#1A365D"),
            alignment=1, # Center
            spaceAfter=20
        )
        
        header_style = ParagraphStyle(
            name="HeaderStyle",
            fontName=font_name,
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#2B6CB0"),
            spaceBefore=10,
            spaceAfter=10
        )
        
        normal_style = ParagraphStyle(
            name="NormalStyle",
            fontName=font_name,
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#2D3748")
        )
        
        table_header_style = ParagraphStyle(
            name="TableHeaderStyle",
            fontName=font_name,
            fontSize=10,
            leading=12,
            textColor=colors.white,
            alignment=1
        )
        
        story = []
        
        # Title
        story.append(Paragraph("销售订单财务分析报告", title_style))
        story.append(Spacer(1, 10))
        
        # Meta info table
        created_time = order.created_at.strftime("%Y-%m-%d %H:%M:%S") if order.created_at else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        meta_data = [
            [
                Paragraph(f"<b>报告编号:</b> FIN-{order.order_number}", normal_style),
                Paragraph(f"<b>生成时间:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style)
            ],
            [
                Paragraph(f"<b>订单编号:</b> {order.order_number}", normal_style),
                Paragraph(f"<b>订单时间:</b> {created_time}", normal_style)
            ]
        ]
        meta_table = Table(meta_data, colWidths=[270, 270])
        meta_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 15))
        
        # Section 1: Customer Details
        story.append(Paragraph("一、 客户基本信息", header_style))
        customer_data = [
            [Paragraph("<b>客户名称:</b>", normal_style), Paragraph(order.customer_name or "N/A", normal_style)],
            [Paragraph("<b>联系方式:</b>", normal_style), Paragraph(order.customer_contact or "N/A", normal_style)],
            [Paragraph("<b>订单状态:</b>", normal_style), Paragraph(order.status or "DRAFT", normal_style)]
        ]
        customer_table = Table(customer_data, colWidths=[100, 440])
        customer_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#F7FAFC")),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
            ('PADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(customer_table)
        story.append(Spacer(1, 15))
        
        # Section 2: Order Breakdown
        story.append(Paragraph("二、 订单款项明细", header_style))
        product_code = order.product.product_code if order.product else "N/A"
        product_name = order.product.name if order.product else "N/A"
        unit_price = float(order.unit_price) if order.unit_price else 0.0
        total_amount = float(order.total_amount) if order.total_amount else 0.0
        
        table_data = [
            [
                Paragraph("<b>产品编码</b>", table_header_style),
                Paragraph("<b>产品名称</b>", table_header_style),
                Paragraph("<b>单价 (元)</b>", table_header_style),
                Paragraph("<b>数量</b>", table_header_style),
                Paragraph("<b>总计金额 (元)</b>", table_header_style)
            ],
            [
                Paragraph(product_code, normal_style),
                Paragraph(product_name, normal_style),
                Paragraph(f"{unit_price:.2f}", normal_style),
                Paragraph(str(order.quantity), normal_style),
                Paragraph(f"{total_amount:.2f}", normal_style)
            ]
        ]
        
        breakdown_table = Table(table_data, colWidths=[100, 160, 90, 80, 110])
        breakdown_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2B6CB0")),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
            ('PADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(breakdown_table)
        story.append(Spacer(1, 20))
        
        # Remark
        if order.remark:
            story.append(Paragraph(f"<b>备注:</b> {order.remark}", normal_style))
            story.append(Spacer(1, 20))
            
        # Section 3: Summary / Signatures
        story.append(Paragraph("三、 审批签章", header_style))
        sig_data = [
            [
                Paragraph("<b>编制人:</b> 财务部系统", normal_style),
                Paragraph("<b>审核人:</b> _________________", normal_style),
                Paragraph("<b>批准人:</b> _________________", normal_style)
            ],
            [
                Paragraph("<b>日期:</b> " + datetime.now().strftime("%Y-%m-%d"), normal_style),
                Paragraph("<b>日期:</b> _________________", normal_style),
                Paragraph("<b>日期:</b> _________________", normal_style)
            ]
        ]
        sig_table = Table(sig_data, colWidths=[180, 180, 180])
        sig_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(sig_table)
        
        # Build PDF
        doc.build(story)
        return file_path
    finally:
        db.close()
