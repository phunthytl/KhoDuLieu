class PivotEngine:
    CUBE_NAME = "DoanhThuBanHang"
    
    MEASURES = {
        "tongtien": {"name": "[Measures].[TongTien]", "label": "Tổng Tiền"},
        "soluong": {"name": "[Measures].[TongSoLuongHang]", "label": "Số Lượng Hàng"},
    }
    
    DIMENSIONS = {
        "vpdd": {"name": "Dim_VPDD", "levels": ["Bang", "TenThanhPho"]},
        "mathang": {"name": "Dim_MatHang", "levels": ["MoTa", "KichCo"]},
        "khachhang": {"name": "Dim_KhachHang", "levels": ["LoaiKhachHang", "TenKhachHang"]},
        "thoigian": {"name": "Dim_ThoiGian", "levels": ["Nam", "Quy", "Thang"]}
    }

    def __init__(self, service):
        self.svc = service

    def build_dynamic_mdx(self, params: dict):
        """
        Build MDX dynamically based on UI params:
        - xAxis: e.g. "thoigian"
        - xLevelIdx: e.g. 0 (Nam), 1 (Quy), 2 (Thang)
        - legend: e.g. "vpdd" (optional)
        - legendLevelIdx: e.g. 0 (Bang)
        - measure: "tongtien" | "soluong"
        - filters: {"vpdd": ["Miền Bắc"], "mathang": ["Ao Thun"]}
        """
        x_axis = params.get("xAxis")
        x_level = int(params.get("xLevelIdx", 0))
        
        legend = params.get("legend")
        legend_level = int(params.get("legendLevelIdx", 0))
        
        measure_id = params.get("measure", "tongtien")
        measure_expr = self.MEASURES[measure_id]["name"]
        
        filters = params.get("filters", {})

        # Build ROWS
        dim_x = self.DIMENSIONS[x_axis]
        lvl_x_name = dim_x["levels"][x_level]
        rows_expr = f"[{dim_x['name']}].[{lvl_x_name}].[{lvl_x_name}].MEMBERS"

        # Build COLUMNS
        cols_expr = f"{{ {measure_expr} }}"
        
        if legend and legend != x_axis:
            dim_leg = self.DIMENSIONS[legend]
            lvl_leg_name = dim_leg["levels"][legend_level]
            # Đưa cả 2 chiều vào ROWS crossjoin
            rows_expr = f"{rows_expr} * [{dim_leg['name']}].[{lvl_leg_name}].[{lvl_leg_name}].MEMBERS"
        else:
            legend = None

        # Build WHERE parameters
        slicer_exprs = []
        for dim_id, members in filters.items():
            if not members: continue
            
            dim_cfg = self.DIMENSIONS[dim_id]
            dim_name = dim_cfg["name"]
            
            if isinstance(members, dict):
                for lvl_name, member_val in members.items():
                    if member_val:
                        slicer_exprs.append(f"[{dim_name}].[{lvl_name}].&[{member_val}]")
            elif isinstance(members, list) and isinstance(members[0], dict):
                # Trường hợp truyền [{level: 'Bang', value: 'Miền Bắc'}]
                for m in members:
                    slicer_exprs.append(f"[{dim_name}].[{m['level']}].&[{m['value']}]")

        from_clause = f"[{self.CUBE_NAME}]"
        
        # Optimize by using Cascading SubSelects instead of WHERE clause
        # This dramatically reduces the cube space before evaluating crossjoins.
        for expr in slicer_exprs:
            from_clause = f"""(
            SELECT {{ {expr} }} ON COLUMNS
            FROM {from_clause}
        )"""
        
        mdx = f"""
        SELECT
            NON EMPTY {cols_expr} ON COLUMNS,
            NON EMPTY {{ {rows_expr} }} ON ROWS
        FROM {from_clause}
        """

        print("---- MDX DYNAMIC ----")
        print(mdx)

        # Execute
        rows = self.svc.execute_mdx(mdx)
        return self._format_result(rows, x_axis, lvl_x_name, legend, dim_leg['levels'][legend_level] if legend else None, measure_id)

    def _format_result(self, rows_arr, x_axis, lvl_x, legend, lvl_leg, measure_id):
        result = []
        for row in rows_arr:
            item = {
                "x": "?",
                "y": "?",
                "value": 0.0
            }
            for k, v in row.items():
                k_lower = k.lower()
                
                # Trích xuất X axis (dòng)
                if lvl_x.lower() in k_lower and 'measures' not in k_lower:
                    item['x'] = str(v) if v else '(All)'
                    
                # Trích xuất nhóm màu (cột)
                elif legend and lvl_leg.lower() in k_lower and 'measures' not in k_lower:
                    item['y'] = str(v) if v else '(All)'
                
                # Trích xuất Measure
                elif measure_id.lower() in k_lower or 'tong' in k_lower or 'value' in k_lower or '[measures]' in k_lower:
                    if isinstance(v, (int, float)):
                        item['value'] = float(v)
                    elif v:
                        try:
                            item['value'] = float(v)
                        except: pass
            
            result.append(item)
            
        return result
