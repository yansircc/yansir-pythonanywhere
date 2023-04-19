from flask import Blueprint, request, render_template, stream_with_context, send_file, Response
from golem import Golem, openai_api_key
from navigator import navigator
from cookies import create_cookie
from queue import Queue
from mdExtensions import HighlightExtension
import genanki
import random
import tempfile
import markdown

anki_cards_blueprint = Blueprint('anki_cards', __name__)
response_queue = Queue()


@anki_cards_blueprint.route('/anki-cards')
@navigator
@create_cookie
def anki_cards():
    form_data = [
        {'label': '待整理文本：', 'tag': 'textarea', 'id': 'user_input', 'name': 'user_input',
            'placeholder': '输入一段想转为Anki卡片的文本', 'rows': '5'},
        {'tag': 'input', 'type': 'submit', 'id': 'submit', 'value': '生成卡片'}
    ]
    endpoint = request.path.lstrip('/')
    return render_template(endpoint+'.jinja2', js_file='js/'+endpoint+'.js', form_data=form_data)


@anki_cards_blueprint.route('/sse/anki_cards', methods=['GET', 'POST'])
def generate_anki_cards():
    if request.method == 'POST':
        session_id = request.cookies.get('user_id')
        user_input = request.form['user_input']
        sys_prompt = """
        You're a Anki card creator who help people create Anki cards for study purpose.
        You're given a text and asked to create a set of flashcards based on the text.
        You can use the text to generate multiple flashcards.
        Each flashcard should contain one question and one answer.
        The question should be specific and unambiguous.
        The answer should be clear and concise.
        The answer should only contain one key fact/name/concept/term.
        You always summarize/rewrite the answer if it is beyond 30 characters.
        You create the flashcards by following the steps below:
        Step 1: Rewrite the content while retaining its original meaning.
        Step 2: Divide the content into several sections, with each section focusing on one point.
        Step 3: Use these sections to generate multiple flashcards.
        For example, here is the original text:
        The characteristics of aging cells are a decrease in water content within the cell, resulting in cell shrinkage and reduced metabolic rate. The activity of various enzymes within the cell is also decreased. The nucleus of the cell increases in size, with folded nuclear membranes and condensed chromatin leading to darker staining. Changes in permeability of the cell membrane result in reduced transport function.
        And here is the JSON format result You output:
        [
            {"How does the volume of aging cells change?": "It decreases."},
            {"What are the specific manifestations of changes in volume for aging cells?": "Cell shrinkage."},
            {"What causes changes in volume for aging cells?": "A decrease in water content within the cell."},
            {"How does a change in water content affect cellular metabolism for aging cells?": "It slows down metabolic rate."},
            {"How does enzyme activity change within an aging cell?": "Activity decreases."},
            {"How does the size of an aging cell's nucleus change?": "It increases."},
            {"How does nuclear membrane morphology change for an aging cell's nucleus?": "It folds inwardly."},
            {"How does chromatin structure change for an aging cell's nucleus?": "It becomes more condensed and stains darker."},
            {"What is the effect on nuclear shape due to changes to chromatin structure for an aging cell's nucleus?": "Darker staining occurs."},
            {"How does transport function change for an ageing-cell ?": "Transport function reduces."},
            {"Why do transport functions reduce as a result from ageing-cells ?": "Permeability changes occur at their cellular membrane."}
        ]
        """
        user_input_prefix = 'Here is the text: '
        user_input_suffix = 'Make sure output in Chinese and JSON format. IMPORTANT: The answer should be straight to the point and under 50 characters.'
        anki_cards_golem = Golem(
            openai_api_key, session_id, sys_prompt=sys_prompt, user_input_prefix=user_input_prefix, user_input_suffix=user_input_suffix)
        response = anki_cards_golem.response(user_input)

        response_queue.put(response)
        return '', 204
    else:
        response = response_queue.get()
        return Response(stream_with_context(response), mimetype='text/event-stream')


@anki_cards_blueprint.route('/generate-apkg', methods=['POST'])
def generate_apkg():
    data = request.get_json()
    model_id = random.randrange(1 << 30, 1 << 31)
    deck_id = random.randrange(1 << 30, 1 << 31)
    my_model = genanki.Model(
        model_id,
        'Simple Model',
        fields=[
            {'name': 'Question'},
            {'name': 'Answer'},
        ],
        templates=[
            {
                'name': 'Card 1',
                'qfmt': '{{Question}}',
                'afmt': '{{Answer}}',
            },
        ])
    my_deck = genanki.Deck(deck_id, 'My Deck')
    highlight_md = markdown.Markdown(extensions=[HighlightExtension()])
    for card in data:
        for question, answer in card.items():
            question=highlight_md.convert(question)
            answer=highlight_md.convert(answer)
            print(question, answer)
            my_deck.add_note(
                genanki.Note(
                    model=my_model,
                    fields=[question, answer]
                )
            )
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    genanki.Package(my_deck).write_to_file(temp_file.name)
    temp_file.close()
    return send_file(temp_file.name, as_attachment=True, download_name='anki_cards.apkg', mimetype='application/octet-stream')


def register_routes(app):
    app.register_blueprint(anki_cards_blueprint)
