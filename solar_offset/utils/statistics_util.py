# Imports
from solar_offset.db import get_db
from .carbon_offset_util import calculate_reduced_carbon_footprint

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import io
import base64


# Public Methods

def calculate_statistics():
    return (get_total_users(),
            get_total_countries(),
            get_number_of_donations(),
            get_total_donations(),
            get_reduced_carbon_emissions())


def get_total_users() -> int:
    # Stored Properties
    db = get_db()
    # Fetching all the user from database
    users = db.execute('SELECT * FROM user').fetchall()
    return len(users) or 0


def get_total_countries() -> int:
    # Stored Properties
    db = get_db()
    # Fetching all the countries listed
    countries = db.execute('SELECT * FROM country').fetchall()
    return len(countries) or 0


def get_number_of_donations() -> int:
    # Stored Properties
    db = get_db()
    # Fetching all the donations made
    donations = db.execute('SELECT * FROM donation').fetchall()
    return len(donations) or 0


def get_total_donations() -> int:
    # Stored Properties
    db = get_db()
    # Fetching all the donations made
    donations = db.execute('SELECT * FROM donation').fetchall()
    # Calculate and returns the total donations made
    return sum(int(donation['donation_amount']) for donation in donations) or 0


def get_reduced_carbon_emissions():
    # Calculate the reduced carbon emission based on total donations made
    return calculate_reduced_carbon_footprint(get_total_donations()) or "0 kg"


def countries_stats(countries):
    # Create the graphs
    solar_hours_chart = create_solar_hours_chart(countries)
    carbon_emissions_chart = create_carbon_emissions_chart(countries)
    solar_panel_price_chart = create_solar_panel_price_chart(countries)
    electricity_mix_chart = create_electricity_mix_chart(countries)
    return solar_hours_chart, carbon_emissions_chart, solar_panel_price_chart, electricity_mix_chart


# Charts
def create_solar_hours_chart(countries):
    # Create a bar chart for solar hours
    country_names = [country['name'] for country in countries]
    solar_hours = [country['solar_hours'] for country in countries]

    fig = plt.figure(figsize=(10, 6), facecolor='#f5f5f5')
    plt.bar(country_names, solar_hours, color='#4CAF50')
    plt.xlabel('Country', fontsize=12)
    plt.ylabel('Solar Hours', fontsize=12)
    plt.title('Solar Hours by Country', fontsize=16, fontweight='bold')
    plt.xticks(rotation=90, fontsize=10)
    plt.yticks(fontsize=10)
    plt.grid(axis='y', linestyle='--', alpha=0.5)

    # Convert the chart to an image
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    solar_hours_chart = base64.b64encode(img.getvalue()).decode('utf-8')

    return solar_hours_chart

def create_carbon_emissions_chart(countries):
    # Create a bar chart for carbon emissions
    country_names = [country['name'] for country in countries]
    carbon_emissions = [country['carbon_emissions'] for country in countries]

    fig = plt.figure(figsize=(10, 6), facecolor='#f5f5f5')
    plt.bar(country_names, carbon_emissions, color='#E53935')
    plt.xlabel('Country', fontsize=12)
    plt.ylabel('Carbon Emissions', fontsize=12)
    plt.title('Carbon Emissions by Country', fontsize=16, fontweight='bold')
    plt.xticks(rotation=90, fontsize=10)
    plt.yticks(fontsize=10)
    plt.grid(axis='y', linestyle='--', alpha=0.5)

    # Convert the chart to an image
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    carbon_emissions_chart = base64.b64encode(img.getvalue()).decode('utf-8')

    return carbon_emissions_chart

def create_solar_panel_price_chart(countries):
    # Create a scatter plot for solar panel price
    country_names = [country['name'] for country in countries]
    solar_panel_price = [country['solar_panel_price_per_kw'] for country in countries]

    fig = plt.figure(figsize=(10, 6), facecolor='#f5f5f5')
    plt.scatter(country_names, solar_panel_price, color='#1E88E5')
    plt.xlabel('Country', fontsize=12)
    plt.ylabel('Solar Panel Price (per kW)', fontsize=12)
    plt.title('Solar Panel Price by Country', fontsize=16, fontweight='bold')
    plt.xticks(rotation=90, fontsize=10)
    plt.yticks(fontsize=10)
    plt.grid(linestyle='--', alpha=0.5)

    # Convert the chart to an image
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    solar_panel_price_chart = base64.b64encode(img.getvalue()).decode('utf-8')

    return solar_panel_price_chart

def create_electricity_mix_chart(countries):
    # Create a pie chart for electricity mix percentage
    country_names = [country['name'] for country in countries]
    electricity_mix_percentage = [country['electricity_mix_percentage'] for country in countries]

    fig = plt.figure(figsize=(8, 8), facecolor='#f5f5f5')
    plt.pie(electricity_mix_percentage, labels=country_names, autopct='%1.1f%%', colors=['#FFA726', '#66BB6A', '#42A5F5', '#EF5350', '#AB47BC'])
    plt.axis('equal')
    plt.title('Electricity Mix Percentage by Country', fontsize=16, fontweight='bold')
    plt.legend(country_names, loc='upper left', fontsize=10)

    # Convert the chart to an image
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    electricity_mix_chart = base64.b64encode(img.getvalue()).decode('utf-8')

    return electricity_mix_chart