from . import app

@app.route('/api/test')
def test_api():
    return {'status': 'ok'}