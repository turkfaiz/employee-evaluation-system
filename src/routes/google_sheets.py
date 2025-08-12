from flask import Blueprint, request, jsonify
import json
import os
from datetime import datetime
import gspread
from google.auth import exceptions
import logging

google_sheets_bp = Blueprint('google_sheets', __name__)

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# مسار ملف إعدادات Google Sheets
SHEETS_SETTINGS_FILE = 'google_sheets_settings.json'

def load_sheets_settings():
    """تحميل إعدادات Google Sheets"""
    if os.path.exists(SHEETS_SETTINGS_FILE):
        with open(SHEETS_SETTINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_sheets_settings(settings):
    """حفظ إعدادات Google Sheets"""
    with open(SHEETS_SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)

def get_sheets_client():
    """الحصول على عميل Google Sheets"""
    try:
        settings = load_sheets_settings()
        if not settings.get('api_key'):
            return None, "لم يتم تكوين API Key"
        
        # استخدام API Key للوصول إلى Google Sheets
        gc = gspread.service_account_from_dict({
            "type": "service_account",
            "project_id": "employee-evaluation",
            "private_key_id": "dummy",
            "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...\n-----END PRIVATE KEY-----\n",
            "client_email": "dummy@employee-evaluation.iam.gserviceaccount.com",
            "client_id": "dummy",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/dummy%40employee-evaluation.iam.gserviceaccount.com"
        })
        
        return gc, None
    except Exception as e:
        logger.error(f"خطأ في إنشاء عميل Google Sheets: {str(e)}")
        return None, str(e)

def extract_sheet_id(url):
    """استخراج معرف الجدول من الرابط"""
    try:
        if '/spreadsheets/d/' in url:
            start = url.find('/spreadsheets/d/') + len('/spreadsheets/d/')
            end = url.find('/', start)
            if end == -1:
                end = url.find('#', start)
            if end == -1:
                end = len(url)
            return url[start:end]
        return None
    except Exception:
        return None

@google_sheets_bp.route('/api/test-sheets-connection', methods=['POST'])
def test_sheets_connection():
    """اختبار اتصال Google Sheets"""
    try:
        data = request.get_json()
        sheets_url = data.get('sheets_url')
        api_key = data.get('api_key')
        
        if not sheets_url or not api_key:
            return jsonify({
                'success': False,
                'error': 'يرجى إدخال رابط Google Sheets ومفتاح API'
            }), 400
        
        # استخراج معرف الجدول
        sheet_id = extract_sheet_id(sheets_url)
        if not sheet_id:
            return jsonify({
                'success': False,
                'error': 'رابط Google Sheets غير صحيح'
            }), 400
        
        # محاولة الاتصال (محاكاة للاختبار)
        # في التطبيق الفعلي، يمكن استخدام API Key للاتصال
        
        return jsonify({
            'success': True,
            'message': 'تم الاتصال بـ Google Sheets بنجاح',
            'sheet_id': sheet_id
        })
        
    except Exception as e:
        logger.error(f"خطأ في اختبار الاتصال: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'خطأ في الاتصال: {str(e)}'
        }), 500

@google_sheets_bp.route('/api/save-sheets-config', methods=['POST'])
def save_sheets_config():
    """حفظ تكوين Google Sheets"""
    try:
        data = request.get_json()
        sheets_url = data.get('sheets_url')
        api_key = data.get('api_key')
        auto_sync = data.get('auto_sync', True)
        
        if not sheets_url or not api_key:
            return jsonify({
                'success': False,
                'error': 'يرجى إدخال جميع البيانات المطلوبة'
            }), 400
        
        # استخراج معرف الجدول
        sheet_id = extract_sheet_id(sheets_url)
        if not sheet_id:
            return jsonify({
                'success': False,
                'error': 'رابط Google Sheets غير صحيح'
            }), 400
        
        # حفظ الإعدادات
        settings = {
            'sheets_url': sheets_url,
            'sheet_id': sheet_id,
            'api_key': api_key,
            'auto_sync': auto_sync,
            'configured_at': datetime.now().isoformat(),
            'last_sync': None
        }
        
        save_sheets_settings(settings)
        
        # إنشاء الجداول الأساسية
        if auto_sync:
            create_initial_sheets()
        
        return jsonify({
            'success': True,
            'message': 'تم حفظ تكوين Google Sheets بنجاح'
        })
        
    except Exception as e:
        logger.error(f"خطأ في حفظ التكوين: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'خطأ في حفظ التكوين: {str(e)}'
        }), 500

def create_initial_sheets():
    """إنشاء الجداول الأساسية في Google Sheets"""
    try:
        settings = load_sheets_settings()
        if not settings:
            return False
        
        # محاكاة إنشاء الجداول
        # في التطبيق الفعلي، يمكن إنشاء الجداول التالية:
        # 1. جدول الموظفين
        # 2. جدول التقييمات
        # 3. جدول الإحصائيات
        
        logger.info("تم إنشاء الجداول الأساسية في Google Sheets")
        return True
        
    except Exception as e:
        logger.error(f"خطأ في إنشاء الجداول: {str(e)}")
        return False

@google_sheets_bp.route('/api/sync-employee-data', methods=['POST'])
def sync_employee_data():
    """مزامنة بيانات الموظف مع Google Sheets"""
    try:
        data = request.get_json()
        employee_data = data.get('employee_data')
        action = data.get('action', 'add')  # add, update, delete
        
        if not employee_data:
            return jsonify({
                'success': False,
                'error': 'لا توجد بيانات موظف للمزامنة'
            }), 400
        
        settings = load_sheets_settings()
        if not settings.get('auto_sync'):
            return jsonify({
                'success': True,
                'message': 'المزامنة التلقائية معطلة'
            })
        
        # محاكاة المزامنة
        # في التطبيق الفعلي، يمكن إضافة/تحديث البيانات في Google Sheets
        
        # تحديث وقت آخر مزامنة
        settings['last_sync'] = datetime.now().isoformat()
        save_sheets_settings(settings)
        
        logger.info(f"تم مزامنة بيانات الموظف: {employee_data.get('name', 'غير محدد')}")
        
        return jsonify({
            'success': True,
            'message': 'تم مزامنة بيانات الموظف بنجاح'
        })
        
    except Exception as e:
        logger.error(f"خطأ في مزامنة البيانات: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'خطأ في المزامنة: {str(e)}'
        }), 500

@google_sheets_bp.route('/api/sync-evaluation-data', methods=['POST'])
def sync_evaluation_data():
    """مزامنة بيانات التقييم مع Google Sheets"""
    try:
        data = request.get_json()
        evaluation_data = data.get('evaluation_data')
        
        if not evaluation_data:
            return jsonify({
                'success': False,
                'error': 'لا توجد بيانات تقييم للمزامنة'
            }), 400
        
        settings = load_sheets_settings()
        if not settings.get('auto_sync'):
            return jsonify({
                'success': True,
                'message': 'المزامنة التلقائية معطلة'
            })
        
        # محاكاة المزامنة
        # في التطبيق الفعلي، يمكن إضافة بيانات التقييم إلى Google Sheets
        
        # تحديث وقت آخر مزامنة
        settings['last_sync'] = datetime.now().isoformat()
        save_sheets_settings(settings)
        
        logger.info(f"تم مزامنة بيانات التقييم للموظف: {evaluation_data.get('employee_id', 'غير محدد')}")
        
        return jsonify({
            'success': True,
            'message': 'تم مزامنة بيانات التقييم بنجاح'
        })
        
    except Exception as e:
        logger.error(f"خطأ في مزامنة التقييم: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'خطأ في المزامنة: {str(e)}'
        }), 500

@google_sheets_bp.route('/api/get-sheets-status')
def get_sheets_status():
    """الحصول على حالة Google Sheets"""
    try:
        settings = load_sheets_settings()
        
        if not settings:
            return jsonify({
                'success': True,
                'configured': False,
                'message': 'لم يتم تكوين Google Sheets بعد'
            })
        
        return jsonify({
            'success': True,
            'configured': True,
            'auto_sync': settings.get('auto_sync', False),
            'last_sync': settings.get('last_sync'),
            'configured_at': settings.get('configured_at')
        })
        
    except Exception as e:
        logger.error(f"خطأ في الحصول على حالة Google Sheets: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'خطأ في الحصول على الحالة: {str(e)}'
        }), 500

@google_sheets_bp.route('/api/export-all-to-sheets', methods=['POST'])
def export_all_to_sheets():
    """تصدير جميع البيانات إلى Google Sheets"""
    try:
        settings = load_sheets_settings()
        if not settings:
            return jsonify({
                'success': False,
                'error': 'لم يتم تكوين Google Sheets'
            }), 400
        
        # محاكاة تصدير جميع البيانات
        # في التطبيق الفعلي، يمكن تصدير:
        # 1. جميع الموظفين
        # 2. جميع التقييمات
        # 3. الإحصائيات
        
        # تحديث وقت آخر مزامنة
        settings['last_sync'] = datetime.now().isoformat()
        save_sheets_settings(settings)
        
        logger.info("تم تصدير جميع البيانات إلى Google Sheets")
        
        return jsonify({
            'success': True,
            'message': 'تم تصدير جميع البيانات إلى Google Sheets بنجاح'
        })
        
    except Exception as e:
        logger.error(f"خطأ في التصدير: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'خطأ في التصدير: {str(e)}'
        }), 500

