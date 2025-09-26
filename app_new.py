"""
EVE Profit Master Backend API
Comprehensive backend for EVE Online production planning application
"""

import os
import secrets
import datetime
from flask import Flask, jsonify, request, redirect, session, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask extensions
db = SQLAlchemy()
cors = CORS()

# Import services and controllers
from services.eve_sso_service import EVESSOService
from services.esi_data_service import ESIDataService
from services.cache_service import CacheService
from services.business_logic_service import BusinessLogicService
from services.market_data_service import MarketDataService

from controllers.auth_controller import AuthController
from controllers.character_controller import CharacterController
from controllers.market_controller import MarketController
from controllers.industry_controller import IndustryController

from models.user import User
from models.project import Project
from models.cache_entry import CacheEntry
from models.market_data import MarketData


def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', secrets.token_hex(16))
    database_url = os.environ.get('DATABASE_URL') or 'postgresql://eve_profitmaster_v2_user:dimISkVaaTRhbCYnLbgNNjnCvudXwRaq@dpg-d39v2lp5pdvs73botp5g-a.frankfurt-postgres.render.com/eve_profitmaster_v2'
    
    if database_url:
        if database_url.startswith("postgresql://"):
            database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)
        elif database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    cors.init_app(app)
    
    # Initialize models
    user_model = User(db).model
    project_model = Project(db).model
    cache_entry_model = CacheEntry(db).model
    market_data_model = MarketData(db).model
    
    # Initialize services
    cache_service = CacheService(db)
    eve_sso_service = EVESSOService(
        os.environ.get('EVE_CLIENT_ID', ''),
        os.environ.get('EVE_SECRET_KEY', '')
    )
    esi_service = ESIDataService(cache_service)
    business_logic_service = BusinessLogicService(esi_service)
    market_service = MarketDataService(cache_service)
    
    # Initialize controllers
    auth_controller = AuthController(eve_sso_service, user_model, db)
    character_controller = CharacterController(esi_service, business_logic_service, auth_controller)
    market_controller = MarketController(market_service)
    industry_controller = IndustryController()
    
    # Helper functions
    def get_working_api_url():
        """Get the working API URL (local or production)"""
        if app.config.get('FLASK_ENV') == 'development':
            return 'http://localhost:5000'
        else:
            return 'https://eve-profitmaster.onrender.com'
    
    # Routes
    @app.route('/')
    def home():
        return "EVE Profit Master Backend API is running!"
    
    @app.route('/health')
    def health():
        try:
            user_count = user_model.query.count()
            return jsonify({
                'status': 'healthy',
                'database_connected': True,
                'user_count': user_count,
                'environment_vars': {
                    'EVE_CLIENT_ID': bool(os.environ.get('EVE_CLIENT_ID')),
                    'EVE_SECRET_KEY': bool(os.environ.get('EVE_SECRET_KEY')),
                    'DATABASE_URL': bool(os.environ.get('DATABASE_URL'))
                }
            })
        except Exception as e:
            return jsonify({
                'status': 'unhealthy',
                'database_connected': False,
                'error': str(e)
            }), 500
    
    # Authentication routes
    @app.route('/login')
    def login():
        """Initiate EVE SSO login"""
        redirect_uri = f"{get_working_api_url()}/callback"
        auth_url = auth_controller.login(redirect_uri)
        return redirect(auth_url)
    
    @app.route('/callback')
    def callback():
        """Handle EVE SSO callback"""
        code = request.args.get('code')
        state = request.args.get('state')
        redirect_uri = f"{get_working_api_url()}/callback"
        
        result = auth_controller.callback(code, state, redirect_uri)
        if 'error' in result:
            return jsonify(result[0]), result[1]
        
        # Redirect to frontend
        if app.config.get('FLASK_ENV') == 'development':
            return redirect('http://localhost:8080/?auth=success')
        else:
            return redirect('https://eve-profitmaster-1.onrender.com/?auth=success')
    
    # API Routes
    @app.route('/api/characters')
    def get_characters():
        """Get list of authenticated characters"""
        return jsonify(auth_controller.get_characters())
    
    @app.route('/api/characters/<int:character_id>/details')
    @auth_controller.require_auth
    def get_character_details(user):
        """Get detailed character information including activity limits"""
        return jsonify(character_controller.get_character_details(user))
    
    @app.route('/api/characters/<int:character_id>/jobs')
    @auth_controller.require_auth
    def get_character_jobs(user):
        """Get character jobs data"""
        return jsonify(character_controller.get_character_jobs(user))
    
    @app.route('/api/characters/<int:character_id>/planets')
    @auth_controller.require_auth
    def get_character_planets(user):
        """Get character planets data"""
        return jsonify(character_controller.get_character_planets(user))
    
    @app.route('/api/characters/<int:character_id>/skills')
    @auth_controller.require_auth
    def get_character_skills(user):
        """Get character skills"""
        return jsonify(character_controller.get_character_skills(user))
    
    @app.route('/api/characters/<int:character_id>/blueprints')
    @auth_controller.require_auth
    def get_character_blueprints(user):
        """Get character blueprints"""
        return jsonify(character_controller.get_character_blueprints(user))
    
    @app.route('/api/characters/<int:character_id>/assets')
    @auth_controller.require_auth
    def get_character_assets(user):
        """Get character assets"""
        return jsonify(character_controller.get_character_assets(user))
    
    @app.route('/api/characters/<int:character_id>/portrait')
    def get_character_portrait(character_id):
        """Get character portrait URL"""
        return jsonify(character_controller.get_character_portrait(character_id))
    
    @app.route('/api/characters/<int:character_id>', methods=['DELETE'])
    def remove_character(character_id):
        """Remove character from database"""
        result = auth_controller.remove_character(character_id)
        if 'error' in result:
            return jsonify(result[0]), result[1]
        return jsonify(result)
    
    @app.route('/api/reset', methods=['POST'])
    def reset_database():
        """Reset database (remove all users)"""
        result = auth_controller.reset_database()
        if 'error' in result:
            return jsonify(result[0]), result[1]
        return jsonify(result)
    
    # Market routes
    @app.route('/api/market/types/<int:type_id>/prices')
    def get_type_prices(type_id):
        """Get prices for a specific type"""
        region_id = request.args.get('region_id', 10000002, type=int)
        return jsonify(market_controller.get_type_prices(type_id, region_id))
    
    @app.route('/api/market/regions/<int:region_id>/orders')
    def get_market_orders(region_id):
        """Get market orders for a region"""
        type_id = request.args.get('type_id', type=int)
        return jsonify(market_controller.get_market_orders(region_id, type_id))
    
    @app.route('/api/market/regions/<int:region_id>/prices')
    def get_market_prices(region_id):
        """Get market prices for a region"""
        return jsonify(market_controller.get_market_prices(region_id))
    
    @app.route('/api/market/calculate-value')
    def calculate_market_value():
        """Calculate market value for a quantity of items"""
        type_id = request.args.get('type_id', type=int)
        quantity = request.args.get('quantity', type=int)
        region_id = request.args.get('region_id', 10000002, type=int)
        
        if not type_id or not quantity:
            return jsonify({'error': 'type_id and quantity are required'}), 400
        
        return jsonify(market_controller.calculate_market_value(type_id, quantity, region_id))
    
    @app.route('/api/market/regions/<int:region_id>')
    def get_region_info(region_id):
        """Get region information"""
        return jsonify(market_controller.get_region_info(region_id))
    
    @app.route('/api/market/groups')
    def get_market_groups():
        """Get market groups"""
        return jsonify(market_controller.get_market_groups())
    
    @app.route('/api/market/groups/<int:group_id>')
    def get_market_group_info(group_id):
        """Get market group information"""
        return jsonify(market_controller.get_market_group_info(group_id))
    
    # Industry routes - Detailed industrial jobs data collection
    @app.route('/api/industry/characters/<int:character_id>/summary')
    def get_character_industry_summary(character_id):
        """Get comprehensive industry summary for a character"""
        user = auth_controller.get_user_by_character_id(character_id)
        if not user:
            return jsonify({'error': 'Character not found'}), 404
        
        if not auth_controller.refresh_access_token(user):
            return jsonify({'error': 'Authentication failed'}), 401
        
        result = industry_controller.get_character_industry_summary(character_id, user.access_token)
        if 'error' in result:
            return jsonify(result), 500
        return jsonify(result)
    
    @app.route('/api/industry/characters/<int:character_id>/jobs/by-activity')
    def get_jobs_by_activity(character_id):
        """Get jobs filtered by activity type"""
        user = auth_controller.get_user_by_character_id(character_id)
        if not user:
            return jsonify({'error': 'Character not found'}), 404
        
        if not auth_controller.refresh_access_token(user):
            return jsonify({'error': 'Authentication failed'}), 401
        
        activity_id = request.args.get('activity_id', type=int)
        result = industry_controller.get_jobs_by_activity(character_id, user.access_token, activity_id)
        if 'error' in result:
            return jsonify(result), 500
        return jsonify(result)
    
    @app.route('/api/industry/characters/<int:character_id>/jobs/by-location')
    def get_jobs_by_location(character_id):
        """Get jobs grouped by location with security analysis"""
        user = auth_controller.get_user_by_character_id(character_id)
        if not user:
            return jsonify({'error': 'Character not found'}), 404
        
        if not auth_controller.refresh_access_token(user):
            return jsonify({'error': 'Authentication failed'}), 401
        
        result = industry_controller.get_jobs_by_location(character_id, user.access_token)
        if 'error' in result:
            return jsonify(result), 500
        return jsonify(result)
    
    @app.route('/api/industry/characters/<int:character_id>/jobs/priority')
    def get_priority_jobs(character_id):
        """Get jobs by priority level"""
        user = auth_controller.get_user_by_character_id(character_id)
        if not user:
            return jsonify({'error': 'Character not found'}), 404
        
        if not auth_controller.refresh_access_token(user):
            return jsonify({'error': 'Authentication failed'}), 401
        
        priority = request.args.get('priority', 'high')
        if priority not in ['high', 'medium', 'low']:
            return jsonify({'error': 'Priority must be high, medium, or low'}), 400
        
        result = industry_controller.get_priority_jobs(character_id, user.access_token, priority)
        if 'error' in result:
            return jsonify(result), 500
        return jsonify(result)
    
    @app.route('/api/industry/characters/<int:character_id>/jobs/attention')
    def get_jobs_needing_attention(character_id):
        """Get jobs that need immediate attention"""
        user = auth_controller.get_user_by_character_id(character_id)
        if not user:
            return jsonify({'error': 'Character not found'}), 404
        
        if not auth_controller.refresh_access_token(user):
            return jsonify({'error': 'Authentication failed'}), 401
        
        result = industry_controller.get_jobs_needing_attention(character_id, user.access_token)
        if 'error' in result:
            return jsonify(result), 500
        return jsonify(result)
    
    @app.route('/api/industry/characters/<int:character_id>/jobs/detailed')
    def get_detailed_jobs(character_id):
        """Get detailed jobs data with all enriched information"""
        user = auth_controller.get_user_by_character_id(character_id)
        if not user:
            return jsonify({'error': 'Character not found'}), 404
        
        if not auth_controller.refresh_access_token(user):
            return jsonify({'error': 'Authentication failed'}), 401
        
        # Get raw jobs data
        jobs = esi_service.get_character_jobs(character_id, user.access_token)
        if not jobs:
            return jsonify({'character_id': character_id, 'jobs': []})
        
        # Process jobs data
        processed_jobs = business_logic_service.process_jobs_data(jobs, character_id)
        
        return jsonify({
            'character_id': character_id,
            'jobs': processed_jobs,
            'total_jobs': len(processed_jobs),
            'active_jobs': len([j for j in processed_jobs if j['status'] == 'active']),
            'completed_jobs': len([j for j in processed_jobs if j['is_completed']])
        })
    
    # Utility routes
    @app.route('/api/types/<int:type_id>')
    def get_type_info(type_id):
        """Get type information"""
        try:
            type_info = esi_service.get_type_info(type_id)
            return jsonify(type_info)
        except Exception as e:
            return jsonify({'error': f'Internal server error: {str(e)}'}), 500
    
    @app.route('/api/locations/<int:location_id>')
    def get_location_info(location_id):
        """Get location information"""
        try:
            location_info = esi_service.get_location_info(location_id)
            return jsonify(location_info)
        except Exception as e:
            return jsonify({'error': f'Internal server error: {str(e)}'}), 500
    
    # Legacy endpoints for backward compatibility
    @app.route('/get_characters')
    def get_characters_legacy():
        return get_characters()
    
    @app.route('/get_character_details/<int:character_id>')
    def get_character_details_legacy(character_id):
        return get_character_details(character_id)
    
    @app.route('/get_jobs')
    def get_jobs_legacy():
        """Get all jobs for all characters (legacy endpoint)"""
        return jsonify(character_controller.get_all_jobs())
    
    @app.route('/get_character_planets/<int:character_id>')
    def get_character_planets_legacy(character_id):
        user = user_model.query.filter_by(character_id=character_id, is_active=True).first()
        if not user:
            return jsonify({'error': 'Character not found'}), 404
        return get_character_planets(user)
    
    @app.route('/get_character_skills/<int:character_id>')
    def get_character_skills_legacy(character_id):
        user = user_model.query.filter_by(character_id=character_id, is_active=True).first()
        if not user:
            return jsonify({'error': 'Character not found'}), 404
        return get_character_skills(user)
    
    @app.route('/get_character_blueprints/<int:character_id>')
    def get_character_blueprints_legacy(character_id):
        user = user_model.query.filter_by(character_id=character_id, is_active=True).first()
        if not user:
            return jsonify({'error': 'Character not found'}), 404
        return get_character_blueprints(user)
    
    @app.route('/get_character_portrait/<int:character_id>')
    def get_character_portrait_legacy(character_id):
        return get_character_portrait(character_id)
    
    @app.route('/get_type_info/<int:type_id>')
    def get_type_info_legacy(type_id):
        return get_type_info(type_id)
    
    @app.route('/get_location_info/<int:location_id>')
    def get_location_info_legacy(location_id):
        return get_location_info(location_id)
    
    @app.route('/remove_character', methods=['POST'])
    def remove_character_legacy():
        character_id = request.get_json().get('character_id')
        if not character_id:
            return jsonify({'error': 'Character ID required'}), 400
        return remove_character(character_id)
    
    @app.route('/reset_database', methods=['POST'])
    def reset_database_legacy():
        return reset_database()
    
    @app.route('/popup_close')
    def popup_close():
        return render_template('popup_close.html')
    
    return app


# Create and configure the app
app = create_app()

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
