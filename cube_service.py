import win32com.client  # type: ignore
import pythoncom
from typing import Dict, List, Any, Optional


import threading

class OLAPService:
    def __init__(self):
        self.conn_str = (
            "Provider=MSOLAP;"
            "Data Source=localhost\\KDL;"
            "Initial Catalog=DW;"
            "Integrated Security=SSPI;"
        )
        self.local = threading.local()

    def get_connection(self):
        # Đảm bảo COM được thiết lập cho thread hiện tại
        if not hasattr(self.local, 'com_initialized'):
            pythoncom.CoInitialize()
            self.local.com_initialized = True
            
        # Tái sử dụng connection cho cùng một thread
        if not hasattr(self.local, 'conn') or self.local.conn is None:
            self.local.conn = win32com.client.Dispatch("ADODB.Connection")
            self.local.conn.Open(self.conn_str)
        return self.local.conn

    # ── Core MDX executor ───────────────────────────────────────────────────
    def execute_mdx(self, mdx: str) -> List[Dict[str, Any]]:
        try:
            conn = self.get_connection()
            rs = win32com.client.Dispatch("ADODB.Recordset")
            rs.Open(mdx, conn)
            data = []
            while not rs.EOF:
                row = {rs.Fields(i).Name: rs.Fields(i).Value
                       for i in range(rs.Fields.Count)}
                data.append(row)
                rs.MoveNext()
            rs.Close()
            return data
        except Exception as e:
            raise Exception(f"MDX execution failed: {str(e)}")

