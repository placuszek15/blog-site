from flask import Flask, render_template, redirect, request
from markupsafe import Markup, escape
from markdown import markdown
import random
from datetime import datetime
import os
import logging

logging.basicConfig(filename='web.log')


app = Flask(__name__)


class NoCommentsError(Exception):
    pass


@app.route("/")
def root():
    return redirect('index')


def change_md_to_html_safe(md):
    return Markup(markdown(escape(md)))

def change_md_to_html_unsafe(md):
    return Markup(markdown(md))


def handle_body(queried_post):
    with open(f'./posts/{queried_post}') as file:
        text_data = file.read()
    return change_md_to_html_unsafe(text_data)


def handle_comments_read(queried_post):
    returned_html = []
    if not os.path.isdir(f'./posts/{queried_post}/comments'):
        raise NoCommentsError
    possible_comments = [f'{post}' for post in
                         os.listdir(f'./posts/{queried_post}/comments')]
    for comment_file in possible_comments:
        with open(f'./posts/{queried_post}/comments/' + comment_file) as comment_file_data:
            nickname, rest = comment_file_data.read().split('|')
            timestamp = rest.split('\n')[0]
            comment_body = '\n'.join(rest.split('\n')[1:])
            returned_html.append(Markup(f'<div> <strong style="padding-right: 10px ;">{escape(nickname)}</strong>')
                                 + Markup(f'<div style="float: right; font-size:10px"> {timestamp} </div> </div> <br>')
                                 + change_md_to_html_safe(comment_body))
    return returned_html


def add_comment(queried_post, form):
    try:
        assert form['nick'] != ''
        assert form['text'] != ''
        #assert not os.path.isdir(f'./posts/{queried_post}/comments')
        filename = f"./posts/{queried_post}comments/{(str(datetime.now())+str(hash(datetime.now()))).replace(' ','_')}"
        with open(filename, 'x') as comment_file:
            comment_file.write(form['nick'])
            comment_file.write(' | ')
            comment_file.write(str(datetime.now()))
            comment_file.write('\n')
            comment_file.write(form['text'])
    except AssertionError:
            pass
    finally:
        return redirect(f'/{queried_post}post_data')

@app.route("/<path:queried_post>", methods=['GET', 'POST'])
def serve(queried_post):
    if request.method == 'GET':
        return serve_post(queried_post)
    elif request.method == 'POST':
        if queried_post.endswith('/post_data'):
            queried_post = queried_post.replace('/post_data', '')
        return add_comment(queried_post, request.form)


def serve_post(queried_post="Hello World"):
    

    text = f"Queried Post {queried_post} does not exist"
    comments = [f'Queried Post {queried_post} does not contain any comments']
    hasComments = False
    posts = [f'{post}' for post in os.listdir('./posts') if os.path.isdir(f'./posts/{post}')]
    if os.path.exists(f'./posts/{queried_post}'):
        text = handle_body(queried_post)
        if queried_post.endswith('/post_data'):
            queried_post = queried_post.replace('/post_data', '')
        try: 
            comments = handle_comments_read(queried_post)
            hasComments = True
        except NoCommentsError:
            pass
    return render_template('main.html',
                           posts=posts,
                           text=text,
                           comments=comments,
                           hasComments=hasComments
                           )

def return_app():
    return app

if __name__ == '__main__':
    sys.exit()
    app.run(host='0.0.0.0', port=80)
