class PivotEngine:
    CUBE_NAME = "DoanhThuBanHang"
    
    MEASURES = {
        "tongtien": {"name": "[Measures].[TongTien]", "label": "Tổng Tiền"},
        "soluong": {"name": "[Measures].[TongSoLuongHang]", "label": "Số Lượng Hàng"},
    }
    
    DIMENSIONS = {
        "vpdd": {"name": "Dim_VPDD", "hier": "VPDD", "levels": ["Bang", "TenThanhPho"]},
        "mathang": {"name": "Dim_MatHang", "hier": "MatHang", "levels": ["MoTa", "KichCo"]},
        "khachhang": {"name": "Dim_KhachHang", "hier": "KhachHang", "levels": ["LoaiKhachHang", "TenKhachHang"]},
        "thoigian": {"name": "Dim_ThoiGian", "hier": "ThoiGian", "levels": ["Nam", "Quy", "Thang"]}
    }

    def __init__(self, service):
        self.svc = service

    def build_dynamic_mdx(self, params: dict):
        x_axis = params.get("xAxis", "thoigian")
        x_level = int(params.get("xLevelIdx", 0))
        legend = params.get("legend")
        legend_level = int(params.get("legendLevelIdx", 0))
        z_axis = params.get("zAxis")
        z_level = int(params.get("zLevelIdx", 0))
        measure_id = params.get("measure", "tongtien")
        measure_expr = self.MEASURES.get(measure_id, self.MEASURES["tongtien"])["name"]
        filters = params.get("filters", {})
        
        cols_expr = f"{{{measure_expr}}}"
        x_dim_filters = filters.get(x_axis, {})
        other_dim_filters = {k: v for k, v in filters.items() if k != x_axis}

        dim_x = self.DIMENSIONS[x_axis]
        lvl_x_name = dim_x["levels"][x_level]
        
        parent_path = ""
        if x_level > 0:
            path_parts = []
            for i in range(x_level):
                lvl_n = dim_x["levels"][i]
                val = x_dim_filters.get(lvl_n)
                if val:
                    if i == 0: path_parts.append(f"[{lvl_n}].&[{val}]")
                    else: path_parts.append(f"[{val}]")
            if path_parts: parent_path = ".".join(path_parts)

        if parent_path:
            x_set = f"{{ [{dim_x['name']}].[{dim_x['hier']}].{parent_path}.CHILDREN }}"
        else:
            x_set = f"DESCENDANTS([{dim_x['name']}].[{dim_x['hier']}], [{dim_x['name']}].[{dim_x['hier']}].[{lvl_x_name}])"

        rows_expr = x_set
        if legend and legend in self.DIMENSIONS:
            dim_leg = self.DIMENSIONS[legend]
            lvl_leg = dim_leg['levels'][legend_level]
            leg_set = f"TOPCOUNT(DESCENDANTS([{dim_leg['name']}].[{dim_leg['hier']}], [{dim_leg['name']}].[{dim_leg['hier']}].[{lvl_leg}]), 10, {measure_expr})"
            rows_expr = f"NONEMPTY({rows_expr} * {leg_set})"
        
        if z_axis and z_axis in self.DIMENSIONS:
            dim_z = self.DIMENSIONS[z_axis]
            lvl_z = dim_z['levels'][z_level]
            z_set = f"TOPCOUNT(DESCENDANTS([{dim_z['name']}].[{dim_z['hier']}], [{dim_z['name']}].[{dim_z['hier']}].[{lvl_z}]), 5, {measure_expr})"
            rows_expr = f"NONEMPTY({rows_expr} * {z_set})"

        slicer_parts = []
        for d_id, f_dict in other_dim_filters.items():
            if d_id not in self.DIMENSIONS: continue
            d_cfg = self.DIMENSIONS[d_id]
            for l_name, v in f_dict.items():
                if v: slicer_parts.append(f"[{d_cfg['name']}].[{d_cfg['hier']}].[{l_name}].&[{v}]")

        where_clause = ""
        if slicer_parts:
            where_clause = f"WHERE ({', '.join(slicer_parts)})" if len(slicer_parts) > 1 else f"WHERE {slicer_parts[0]}"

        mdx = f"""
        SELECT 
            NON EMPTY {cols_expr} ON COLUMNS,
            NON EMPTY {{ {rows_expr} }} ON ROWS
        FROM [{self.CUBE_NAME}]
        {where_clause}
        """

        rows = self.svc.execute_mdx(mdx) or []
        
        format_meta = {
            "x_axis": x_axis,
            "x_dim": dim_x['name'],
            "x_level_idx": x_level,
            "leg_dim": self.DIMENSIONS[legend]['name'] if legend else None,
            "z_dim": self.DIMENSIONS[z_axis]['name'] if z_axis else None,
            "legend_id": legend,
            "z_axis_id": z_axis
        }
        
        data = self._format_result(rows, format_meta, measure_id)
        return data, mdx

    def _format_result(self, rows_arr, meta, measure_id):
        x_map, x_labels, series_map = {}, [], {}
        if not isinstance(rows_arr, list): rows_arr = []

        x_axis = meta['x_axis']
        x_dim_name = meta['x_dim']
        x_level_idx = meta['x_level_idx']
        leg_dim_name = meta['leg_dim']
        z_dim_name = meta['z_dim']
        dim_x_cfg = self.DIMENSIONS[x_axis]

        for row in rows_arr:
            raw_x, raw_y, raw_z, val = "?", "Tổng", "", 0.0
            if not isinstance(row, dict): continue
            
            is_all = False
            for v in row.values():
                v_s = str(v).lower()
                if v_s == "all" or v_s == "(all)" or "[all]" in v_s:
                    is_all = True
                    break
            if is_all: continue

            # 1. XÂY DỰNG NHÃN X (FULL PATH: 2022 - Quy 1 - Thang 1)
            x_parts = []
            for i in range(x_level_idx + 1):
                l_n = dim_x_cfg['levels'][i]
                for k, v in row.items():
                    if x_dim_name.lower() in k.lower() and f"[{l_n.lower()}]" in k.lower():
                        cleaned = self._clean_label(v, x_axis, l_n)
                        if cleaned: x_parts.append(cleaned)
                        break
            if x_parts: raw_x = " - ".join(x_parts)

            # 2. Tìm nhãn Legend
            if leg_dim_name:
                for k, v in row.items():
                    if leg_dim_name.lower() in k.lower() and 'measures' not in k.lower():
                        raw_y = self._clean_label(v, meta['legend_id'], "Legend")
                        break
            
            # 3. Tìm nhãn Z-Axis
            if z_dim_name:
                for k, v in row.items():
                    if z_dim_name.lower() in k.lower() and 'measures' not in k.lower():
                        raw_z = self._clean_label(v, meta['z_axis_id'], "ZAxis")
                        break

            # 4. Tìm Measure
            for k, v in row.items():
                k_l = k.lower()
                if measure_id.lower() in k_l or 'tong' in k_l or '[measures]' in k_l:
                    try: val = float(v) if v is not None else 0.0
                    except: val = 0.0
                    break

            if raw_x == "?": continue
            
            # Key định danh duy nhất cho series (bao gồm cả leg_val và z_val)
            series_key = f"{raw_y}||{raw_z}"

            if raw_x not in x_map:
                x_map[raw_x] = len(x_labels)
                x_labels.append(raw_x)
            
            idx = x_map[raw_x]
            if series_key not in series_map: 
                series_map[series_key] = {
                    "name": f"{raw_y} - {raw_z}" if raw_z else raw_y,
                    "leg_val": raw_y,
                    "z_val": raw_z or "-",
                    "data": {}
                }
            series_map[series_key]["data"][idx] = series_map[series_key]["data"].get(idx, 0) + val

        # Sắp xếp nhãn trục X nếu là thời gian
        final_x = sorted(x_labels, key=self._sort_key) if x_axis == 'thoigian' else x_labels
        
        final_series = []
        for s_key, s_obj in series_map.items():
            final_series.append({
                "name": s_obj["name"],
                "leg_val": s_obj["leg_val"],
                "z_val": s_obj["z_val"],
                "data": [s_obj["data"].get(x_map[lx], 0) for lx in final_x]
            })

        return {"x_labels": final_x, "series": final_series}

    def _clean_label(self, val, dim_id, lvl_name):
        s = str(val) if val is not None else ""
        if dim_id == 'thoigian' and s.isdigit():
            v = int(s)
            if lvl_name.lower() == 'quy': return f"Quý {v}"
            if lvl_name.lower() == 'thang': return f"Tháng {v}"
        return s

    def _sort_key(self, label):
        import re
        nums = re.findall(r'\d+', label)
        # Sắp xếp theo chuỗi số (Năm -> Quý -> Tháng)
        return [int(n) for n in nums] if nums else [0]
