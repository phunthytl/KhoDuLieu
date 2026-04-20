from flask import Flask, render_template, request, jsonify
from cube_service import OLAPService
import json
from datetime import datetime

app = Flask(__name__)
olap_service = OLAPService()

# ==================== HOME PAGE ====================
@app.route('/')
def home():
    """Trang chủ (Pivot Dashboard Duy Nhất)"""
    return render_template('dashboard.html')

from mdx_builder import PivotEngine

pivot_engine = PivotEngine(olap_service)

# ==================== GENERIC OLAP EXPLORER API ====================

@app.route('/api/pivot', methods=['POST'])
def pivot_query():
    """API sinh MDX Pivot Động 4 Chiều"""
    try:
        params = request.get_json(force=True) or {}
        # Payload bao gồm: xAxis, xLevelIdx, legend, legendLevelIdx, measure, filters
        data, mdx = pivot_engine.build_dynamic_mdx(params)
        return jsonify({'success': True, 'data': data, 'mdx': mdx})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== ERROR HANDLERS ====================
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# ==================== STARTUP ====================
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
