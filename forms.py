from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, validators
from wtforms.validators import DataRequired, Email, Length

class SimulationForm(FlaskForm):
    """form for running simulation"""
    ticker = StringField('Ticker Symbol')
    EMAres = IntegerField('EMA Resolution', validators = [validators.NumberRange(min=15, max=25)])
    STDmult = FloatField('σ Multiplier', validators = [validators.NumberRange(min=0.5,max=3.0)])