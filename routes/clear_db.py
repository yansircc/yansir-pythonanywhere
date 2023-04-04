from flask import Blueprint, request, jsonify
from transcripts_db import TranscriptsDB

clear_transcript_history_blueprint = Blueprint(
    'clear_transcript_history', __name__)


@clear_transcript_history_blueprint.route('/clear_transcript_history')
def clear_transcript_history():
    session_id = request.args.get('session_id', '')
    table_name = request.args.get('table_name', '')
    column_name = request.args.get('column_name', '')

    clear_db = TranscriptsDB()

    with clear_db as db:
        db.clear_data('conversation', session_id, 'transcript_history')

    return jsonify({'message': 'Transcript history cleared', 'success': True}), 200


def register_routes(app):
    app.register_blueprint(clear_transcript_history_blueprint)
