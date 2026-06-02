from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.constants import TraceActionType, TraceSourceType, TraceTargetType
from app.core.database import get_db
from app.apps.traceability.models import TraceabilityRecord

router = APIRouter()

# 样式常量，避免每次请求重复创建字典
_STYLE_ERP = {"background": "rgba(59, 130, 246, 0.1)", "border": "1px solid #3b82f6", "color": "#fff", "borderRadius": "8px", "padding": "10px"}
_STYLE_MES = {"background": "rgba(16, 185, 129, 0.1)", "border": "1px solid #10b981", "color": "#fff", "borderRadius": "8px", "padding": "10px"}
_STYLE_WMS = {"background": "rgba(245, 158, 11, 0.1)", "border": "1px solid #f59e0b", "color": "#fff", "borderRadius": "8px", "padding": "10px"}


@router.get("/graph/{product_barcode}")
def get_traceability_graph(product_barcode: str, db: Session = Depends(get_db)):
    """根据成品的条码，获取其完整生产和溯源树。"""
    records = (
        db.query(TraceabilityRecord)
        .filter(
            TraceabilityRecord.target_barcode == product_barcode,
            TraceabilityRecord.target_type == TraceTargetType.PRODUCT,
        )
        .all()
    )

    if not records:
        raise HTTPException(status_code=404, detail="Traceability record not found")

    nodes: list[dict] = []
    edges: list[dict] = []
    added_node_ids: set[str] = set()  # 用于节点去重

    def _add_node(node_id: str, node_data: dict) -> None:
        if node_id not in added_node_ids:
            nodes.append(node_data)
            added_node_ids.add(node_id)

    # 1. 产成品节点 (ERP)
    product_node_id = f"product-{product_barcode}"
    _add_node(product_node_id, {
        "id": product_node_id,
        "type": "custom",
        "data": {"label": f"Product: {product_barcode}", "type": "ERP - Finished Good", "quantity": 1},
        "style": _STYLE_ERP,
    })

    # 获取唯一的工单ID
    wo_ids = {r.work_order_id for r in records if r.work_order_id}

    for wo_id in wo_ids:
        # 2. 工单节点 (MES)
        wo_node_id = f"wo-{wo_id}"
        _add_node(wo_node_id, {
            "id": wo_node_id,
            "type": "custom",
            "data": {"label": f"Work Order ID: {wo_id}", "type": "MES - Work Order"},
            "style": _STYLE_MES,
        })

        # 产出连线 (MES -> ERP)
        edges.append({
            "id": f"edge-wo{wo_id}-prod{product_barcode}",
            "source": wo_node_id,
            "target": product_node_id,
            "animated": True,
            "style": {"stroke": "#3b82f6"},
            "label": "PRODUCES",
        })

    for r in records:
        if r.source_type == TraceSourceType.MATERIAL:
            # 3. 物料节点 (WMS) - 通过 set 去重
            mat_node_id = f"mat-{r.source_barcode}"
            _add_node(mat_node_id, {
                "id": mat_node_id,
                "type": "custom",
                "data": {"label": f"Material: {r.source_barcode}", "type": "WMS - Raw Material"},
                "style": _STYLE_WMS,
            })

            # 消耗连线 (WMS -> MES)
            edge_id = f"edge-mat{r.source_barcode}-wo{r.work_order_id}"
            # 连线也可能重复，同样去重
            if not any(e["id"] == edge_id for e in edges):
                edges.append({
                    "id": edge_id,
                    "source": mat_node_id,
                    "target": f"wo-{r.work_order_id}",
                    "animated": True,
                    "style": {"stroke": "#10b981"},
                    "label": "CONSUMES",
                })

    return {"nodes": nodes, "edges": edges}
