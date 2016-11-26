from flask import Blueprint, current_app, render_template, url_for, redirect,\
    request, session, flash
from slacker import Slacker, Error
from flask_login import login_user
import model
import peewee
import logging
import spacewiki.model
from dispatcher import make_wiki_app
import stripe

BLUEPRINT = Blueprint('routes', __name__)

@BLUEPRINT.app_context_processor
def add_site_settings():
    return dict(settings=current_app.config)

@BLUEPRINT.route('/')
@BLUEPRINT.route('/<path>')
def index(path=None):
    if current_app.config['DEADSPACE']:
        return render_template('deadspace.html')
    else:
        return render_template('index.html')

@BLUEPRINT.route('/slack_add_flow')
def add_to_slack():
    try:
        slacker = consume_token(url_for('routes.add_to_slack', _external=True))
    except Error, e:
        flash("There was an error logging you in: %s"%e)
        return redirect(url_for('routes.index'))
    if slacker is None:
        flash('You denied the request to login')
        return redirect(url_for('routes.index'))
    space = model.Space.from_team_slacker(slacker)
    slack_team = slacker.api.get('team.info').body
    logging.debug("Found space for %s. Active: %s", space.slack_team_id,
            space.active)
    if space.active:
        return redirect('https://%s.spacewiki.io/'%(domain))
    model.Space.make_space_database(slack_team['team']['id'])
    session['slack_team'] = slack_team['team']['id']
    return redirect(url_for('routes.signup'))

@BLUEPRINT.route('/slack_login_flow')
def slack_login():
    try:
        slacker = consume_token(url_for('routes.slack_login', _external=True))
    except Error, e:
        flash("There was an error logging in: %s"%e)
        return redirect(url_for('routes.index'))
    if slacker is None:
        flash('You denied the request to login')
        return redirect(url_for('routes.index'))
    space = model.Space.from_user_slacker(slacker)
    if space is not None:
        user_id = slacker.api.get('users.identity').body
        handle = slacker.api.get('auth.test').body['user']
        slack_id = user_id['user']['id']
        space_app = make_wiki_app(space.domain)
        with space_app.app_context():
            user_id = login_slack_id(slack_id)
            user_id.display_name = user_id['user']['name']
            user_id.handle = handle
            user_id.save()
        return redirect('https://%s.spacewiki.io/'%(domain))
    else:
        flash("Your team doesn't have a wiki yet!")
        return redirect(url_for('routes.index'))

@BLUEPRINT.route('/signup')
def signup():
    return render_template('signup.html')

@BLUEPRINT.route('/signup/<plan>')
def choose_plan(plan):
    slack_team_id = session.get('slack_team', None)
    space = model.Space.get(slack_team_id=slack_team_id)
    session['plan_type'] = plan
    if plan == 'free':
        space.active = True
        space.save()
        return redirect(url_for('routes.finished'))
    return render_template('pay.html', plan=plan, space=space)

@BLUEPRINT.route('/payment', methods=['POST'])
def payment():
    slack_team_id = session.get('slack_team', None)
    plan_type = session.get('plan_type', None)
    space = model.Space.get(slack_team_id=slack_team_id)
    subscription_id = None
    if plan_type == 'startup':
        subscription_id = 'startup'
    if plan_type == 'corporate':
        subscription_id = 'corporate'
    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']

    stripe_token = request.form['stripeToken']

    if space.stripe_customer_id == '':
        customer = stripe.Customer.create(source=stripe_token)
        space.stripe_customer_id = customer.id
    
    logging.debug("Processing new subscription for %s plan", plan_type)
    # plan == None means they picked the 'donate' button
    if subscription_id is not None:
        sub = stripe.Subscription.create(
            customer = space.stripe_customer_id,
            plan=subscription_id
        )
        space.stripe_subscription_id = sub.id
    else:
        donation_value = int(float(request.form['donationValue']) * 100)
        stripe.Charge.create(
            customer = space.stripe_customer_id,
            amount = donation_value,
            currency = 'USD'
        )

    space.active = True
    space.save()
    return redirect(url_for('routes.finished'))

@BLUEPRINT.route('/welcome')
def finished():
    slack_team_id = session.get('slack_team', None)
    space = model.Space.get(slack_team_id=slack_team_id)
    return render_template('finished.html', space=space)

def login_slack_id(slack_id):
    try:
        identity = spacewiki.model.Identity.get(spacewiki.model.Identity.auth_id == slack_id,
                spacewiki.model.Identity.auth_type == 'slack')
    except:
        identity = spacewiki.model.Identity.create(
                auth_id=slack_id,
                auth_type='slack',
                display_name='',
                handle=slack_id
        )
    login_user(identity)
    return identity

def consume_token(uri):
    login_code = request.args.get('code', None)
    if login_code is None:
        return None
    resp = Slacker.oauth.access(current_app.config['SLACK_KEY'],
            current_app.config['SLACK_SECRET'], login_code, uri).body
    return Slacker(resp['access_token'])
