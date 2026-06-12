import os
from decimal import Decimal
import pytest
from app.tasks.report import generate_report
from app.apps.erp.models import SalesOrder, Product

def test_generate_report_success(db):
    # 1. Create a dummy product
    product = Product(
        product_code="PROD-TEST-123",
        name="测试测试产品",
        price=Decimal("150.00"),
        unit="个",
        description="用于单元测试的测试产品"
    )
    db.add(product)
    db.commit()
    
    # 2. Create a dummy sales order linked to that product
    sales_order = SalesOrder(
        order_number="SO-TEST-2026",
        customer_name="测试客户张三",
        customer_contact="13800138000",
        product_id=product.id,
        quantity=5,
        unit_price=Decimal("150.00"),
        total_amount=Decimal("750.00"),
        status="CONFIRMED",
        remark="测试订单备注说明"
    )
    db.add(sales_order)
    db.commit()
    
    # Override SessionLocal in the task to use our test db session
    # The task opens db using SessionLocal from app.core.database.
    # To intercept that in tests, we can mock the SessionLocal in the report module.
    import app.tasks.report
    # Save original SessionLocal
    orig_session_local = app.tasks.report.SessionLocal
    # Override with lambda returning our test db session
    app.tasks.report.SessionLocal = lambda: db
    
    try:
        # Run task synchronously (calling it directly)
        # Note: we need to pass task request object or mock self.request.id
        # Let's mock the request.id on the task object, or since we decorated it with @celery_app.task(bind=True),
        # calling it directly generate_report(order_id) without celery might need to mock the self argument,
        # but wait! If we call it via .apply(args=[order_id]), Celery will execute it synchronously and handle 'self'.
        # Or even simpler: we can call it using generate_report.apply(args=(sales_order.id,)).result or similar.
        # Let's try calling it using generate_report.apply(args=(sales_order.id,)) which binds 'self' automatically!
        result = generate_report.apply(args=(sales_order.id,))
        
        # Check task result is successful
        assert result.successful()
        
        file_path = result.result
        assert file_path is not None
        assert os.path.exists(file_path)
        assert file_path.endswith(".pdf")
        assert os.path.getsize(file_path) > 0
        
        # Cleanup file after test
        if os.path.exists(file_path):
            os.remove(file_path)
            
    finally:
        # Restore SessionLocal
        app.tasks.report.SessionLocal = orig_session_local
