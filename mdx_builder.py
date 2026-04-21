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
        dim_x = self.DIMENSIONS[x_axis]
        lvl_x_name = dim_x["levels"][x_level]

        def get_parent_path(dim_id, level_idx):
            dim_cfg = self.DIMENSIONS[dim_id]
            dim_filters = filters.get(dim_id, {})
            if level_idx > 0:
                deepest_lvl = dim_cfg["levels"][level_idx - 1]
                val = dim_filters.get(deepest_lvl)
                if val:
                    if isinstance(val, list): val = val[0] # Chỉ lấy 1 giá trị khi drill-down
                    composite_key = ""
                    if dim_id == 'thoigian':
                        nam = dim_filters.get('Nam', '')
                        if isinstance(nam, list): nam = nam[0]
                        quy = dim_filters.get('Quy', '')
                        if isinstance(quy, list): quy = quy[0]
                        thang = dim_filters.get('Thang', '')
                        if isinstance(thang, list): thang = thang[0]
                        
                        if deepest_lvl == 'Nam': composite_key = f"&[{nam}]"
                        elif deepest_lvl == 'Quy': composite_key = f"&[{nam}]&[{quy}]"
                        elif deepest_lvl == 'Thang': composite_key = f"&[{thang}]&[{quy}]&[{nam}]"
                    else:
                        composite_key = f"&[{val}]"
                    return f"[{deepest_lvl}].{composite_key}"
            return ""

        # 1. XÂY DỰNG TRỤC X
        dim_x = self.DIMENSIONS[x_axis]
        lvl_x_name = dim_x["levels"][x_level]
        top_x = 30 if x_axis == 'mathang' else 50
        if x_axis == 'thoigian': top_x = 100
        
        x_parent_path = get_parent_path(x_axis, x_level)
        if x_parent_path:
            x_set = f"TOPCOUNT({{ [{dim_x['name']}].[{dim_x['hier']}].{x_parent_path}.CHILDREN }}, {top_x}, {measure_expr})"
        else:
            x_set = f"TOPCOUNT(DESCENDANTS([{dim_x['name']}].[{dim_x['hier']}], [{dim_x['name']}].[{dim_x['hier']}].[{lvl_x_name}]), {top_x}, {measure_expr})"

        # 2. XÂY DỰNG TRỤC ROWS (LEGEND & Z)
        active_sets = [x_set]
        used_dims = {x_axis}
        
        if legend and legend in self.DIMENSIONS and legend not in used_dims:
            dim_leg = self.DIMENSIONS[legend]
            lvl_leg = dim_leg['levels'][legend_level]
            top_leg = 30 if legend == 'mathang' else 50
            leg_parent_path = get_parent_path(legend, legend_level)
            if leg_parent_path:
                active_sets.append(f"TOPCOUNT({{ [{dim_leg['name']}].[{dim_leg['hier']}].{leg_parent_path}.CHILDREN }}, {top_leg}, {measure_expr})")
            else:
                active_sets.append(f"TOPCOUNT(DESCENDANTS([{dim_leg['name']}].[{dim_leg['hier']}], [{dim_leg['name']}].[{dim_leg['hier']}].[{lvl_leg}]), {top_leg}, {measure_expr})")
            used_dims.add(legend)
        
        if z_axis and z_axis in self.DIMENSIONS and z_axis not in used_dims:
            dim_z = self.DIMENSIONS[z_axis]
            lvl_z = dim_z['levels'][z_level]
            top_z = 30 if z_axis == 'mathang' else 50
            z_parent_path = get_parent_path(z_axis, z_level)
            if z_parent_path:
                active_sets.append(f"TOPCOUNT({{ [{dim_z['name']}].[{dim_z['hier']}].{z_parent_path}.CHILDREN }}, {top_z}, {measure_expr})")
            else:
                active_sets.append(f"TOPCOUNT(DESCENDANTS([{dim_z['name']}].[{dim_z['hier']}], [{dim_z['name']}].[{dim_z['hier']}].[{lvl_z}]), {top_z}, {measure_expr})")
            used_dims.add(z_axis)

        rows_expr = " * ".join(active_sets)
        if len(active_sets) > 1:
            rows_expr = f"NONEMPTY({rows_expr})"

        # 3. XÂY DỰNG BỘ LỌC (SLICERS)
        main_slicers = []   # Cho biểu đồ
        total_slicers = []  # Cho ô số tổng
        
        for d_id, f_dict in filters.items():
            if d_id not in self.DIMENSIONS: continue
            d_cfg = self.DIMENSIONS[d_id]
            
            deepest_lvl = None
            for l_name in d_cfg['levels']:
                if f_dict.get(l_name): deepest_lvl = l_name
            
            if deepest_lvl:
                val = f_dict[deepest_lvl]
                if not val: continue
                
                def build_member_paths(lvl_name, value_list, parent_suffix=""):
                    v_list = value_list if isinstance(value_list, list) else [value_list]
                    return [f"[{d_cfg['name']}].[{d_cfg['hier']}].[{lvl_name}].&[{v}]{parent_suffix}" for v in v_list]
                
                paths = []
                if d_id == 'thoigian':
                    nam = f_dict.get('Nam', '')
                    quy = f_dict.get('Quy', '')
                    thang = f_dict.get('Thang', '')
                    
                    nam_str = nam[0] if isinstance(nam, list) else nam
                    quy_str = quy[0] if isinstance(quy, list) else quy
                    
                    if deepest_lvl == 'Nam': 
                        paths = build_member_paths('Nam', nam)
                    elif deepest_lvl == 'Quy': 
                        paths = build_member_paths('Quy', quy, f"&[{nam_str}]")
                    elif deepest_lvl == 'Thang': 
                        paths = build_member_paths('Thang', thang, f"&[{quy_str}]&[{nam_str}]")
                else:
                    paths = build_member_paths(deepest_lvl, val)
                
                if not paths: continue
                
                slicer_expr = paths[0] if len(paths) == 1 else "{ " + ", ".join(paths) + " }"
                
                total_slicers.append(slicer_expr)
                main_slicers.append(slicer_expr)
        
        # 4. TẠO FROM CLAUSE
        from_main = f"[{self.CUBE_NAME}]"
        for s in main_slicers:
            from_main = f"(SELECT ({s}) ON 0 FROM {from_main})"
            
        from_summary = f"[{self.CUBE_NAME}]"
        for s in total_slicers:
            from_summary = f"(SELECT ({s}) ON 0 FROM {from_summary})"

        # 5. TẠO CÂU LỆNH MDX CHÍNH
        mdx_main = f"SELECT NON EMPTY {cols_expr} ON COLUMNS, NON EMPTY {{ {rows_expr} }} ON ROWS FROM {from_main}"
        print(f"\n--- OLAP ENGINE EXECUTING ---\n{mdx_main}\n")
        
        main_rows = self.svc.execute_mdx(mdx_main) or []
        
        # 6. TRUY VẤN SUMMARY (KPIs)
        mdx_summary = f"SELECT {{[Measures].[TongTien], [Measures].[TongSoLuongHang]}} ON 0 FROM {from_summary}"
        print(f"DEBUG SUMMARY MDX: {mdx_summary}")
        summary_rows = self.svc.execute_mdx(mdx_summary) or []
        summary_data = {"tongtien": 0, "soluong": 0}
        if summary_rows and isinstance(summary_rows[0], dict):
            for k, v in summary_rows[0].items():
                if 'tongtien' in k.lower(): summary_data["tongtien"] = v
                if 'tongsoluonghang' in k.lower(): summary_data["soluong"] = v

        format_meta = {
            "x_axis": x_axis, "x_dim": dim_x['name'], "x_level_idx": x_level,
            "leg_dim": self.DIMENSIONS[legend]['name'] if legend and legend in self.DIMENSIONS else None,
            "z_dim": self.DIMENSIONS[z_axis]['name'] if z_axis and z_axis in self.DIMENSIONS else None,
            "legend_id": legend, "z_axis_id": z_axis
        }
        
        data = self._format_result(main_rows, format_meta, measure_id)
        data["summary"] = summary_data
        return data, mdx_main

    def _format_result(self, rows_arr, meta, measure_id):
        x_map, x_labels, series_map = {}, [], {}
        if not isinstance(rows_arr, list): rows_arr = []

        x_axis, x_dim_name, x_level_idx = meta['x_axis'], meta['x_dim'], meta['x_level_idx']
        leg_dim_name, z_dim_name = meta['leg_dim'], meta['z_dim']
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

            x_parts = []
            for i in range(x_level_idx + 1):
                l_n = dim_x_cfg['levels'][i]
                for k, v in row.items():
                    if x_dim_name.lower() in k.lower() and f"[{l_n.lower()}]" in k.lower():
                        cleaned = self._clean_label(v, x_axis, l_n)
                        if cleaned: x_parts.append(cleaned)
                        break
            if x_parts: raw_x = " - ".join(x_parts)

            if leg_dim_name:
                for k, v in row.items():
                    if leg_dim_name.lower() in k.lower() and 'measures' not in k.lower():
                        raw_y = self._clean_label(v, meta['legend_id'], "Legend")
                        break
            if z_dim_name:
                for k, v in row.items():
                    if z_dim_name.lower() in k.lower() and 'measures' not in k.lower():
                        raw_z = self._clean_label(v, meta['z_axis_id'], "ZAxis")
                        break

            for k, v in row.items():
                k_l = k.lower()
                if measure_id.lower() in k_l or 'tong' in k_l or '[measures]' in k_l:
                    try: val = float(v) if v is not None else 0.0
                    except: val = 0.0
                    break

            if raw_x == "?": continue
            series_key = f"{raw_y}||{raw_z}"

            if raw_x not in x_map:
                x_map[raw_x] = len(x_labels)
                x_labels.append(raw_x)
            
            idx = x_map[raw_x]
            if series_key not in series_map: 
                series_map[series_key] = {
                    "name": f"{raw_y} - {raw_z}" if raw_z else raw_y,
                    "leg_val": raw_y, "z_val": raw_z or "-", "data": {}
                }
            series_map[series_key]["data"][idx] = series_map[series_key]["data"].get(idx, 0) + val

        # Sắp xếp Trục X (Thời gian luôn cần sắp xếp, các chiều khác giữ nguyên)
        final_x = sorted(x_labels, key=self._sort_key) if x_axis == 'thoigian' else x_labels
        
        # Sắp xếp các Series (Legend) một cách triệt để
        sorted_series_keys = sorted(series_map.keys(), key=lambda k: self._sort_key(series_map[k]["name"]))
        
        final_series = []
        for s_key in sorted_series_keys:
            s_obj = series_map[s_key]
            final_series.append({
                "name": s_obj["name"],
                "leg_val": s_obj["leg_val"],
                "z_val": s_obj["z_val"],
                "data": [s_obj["data"].get(x_map[lx], 0) for lx in final_x]
            })

        return {"x_labels": final_x, "series": final_series}

    def _clean_label(self, val, dim_id, lvl_name):
        """Làm sạch nhãn và thêm tiền tố Quý/Tháng nếu cần"""
        if val is None: return ""
        s = str(val).strip()
        
        # Nếu là đường dẫn MDX đầy đủ, lấy phần tử cuối cùng trong &[...]
        import re
        if ".&[" in s:
            match = re.search(r'\.&\[([^\]]+)\]', s)
            if match: s = match.group(1)
        
        # Xử lý riêng cho chiều Thời gian
        if dim_id == 'thoigian' and s.isdigit():
            v = int(s)
            l_n = str(lvl_name).lower()
            if 'quy' in l_n: return f"Quý {v}"
            if 'thang' in l_n: return f"Tháng {v}"
        return s

    def _sort_key(self, text):
        """Thuật toán Natural Sort: Chia chuỗi thành các phần số và chữ để so sánh chuẩn"""
        import re
        def convert(t): return int(t) if t.isdigit() else t.lower()
        return [convert(c) for c in re.split(r'(\d+)', str(text))]
