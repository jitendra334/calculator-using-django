from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
import json
import math
import re
from .models import Calculation
from .forms import UserRegistrationForm, UserLoginForm

def get_operation_type(expression):
    """Detect the primary operation type from the expression"""
    # Remove spaces
    expr = expression.replace(' ', '')
    
    # Check for operations in order of priority
    if '/' in expr:
        return 'divide'
    elif '*' in expr:
        return 'multiply'
    elif expr.count('+') > expr.count('-') or ('+' in expr and '-' not in expr):
        return 'add'
    elif '-' in expr and expr[0] != '-':  # Exclude negative sign at start
        return 'subtract'
    elif 'sqrt' in expr:
        return 'sqrt'
    elif 'sin' in expr:
        return 'sin'
    elif 'cos' in expr:
        return 'cos'
    elif 'tan' in expr:
        return 'tan'
    elif 'log' in expr:
        return 'log'
    elif '^' in expr or '**' in expr:
        return 'power'
    else:
        return 'other'

def index(request):
    return render(request, 'calculator/index.html')

@csrf_exempt
def calculate(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            expression = data.get('expression', '')
            
            # Security: Remove any potentially dangerous characters
            safe_expression = expression.replace(' ', '')
            
            # Handle special cases
            if '^' in safe_expression:
                safe_expression = safe_expression.replace('^', '**')
            
            # Define safe functions and constants
            safe_dict = {
                'sqrt': math.sqrt,
                'sin': math.sin,
                'cos': math.cos,
                'tan': math.tan,
                'log': math.log,
                'log10': math.log10,
                'pi': math.pi,
                'e': math.e,
                'abs': abs,
                'round': round,
            }
            
            # Evaluate safely
            result = eval(safe_expression, {"__builtins__": None}, safe_dict)
            
            # Format result
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            
            # Save to database if user is authenticated
            if request.user.is_authenticated:
                operation_type = get_operation_type(expression)
                Calculation.objects.create(
                    user=request.user,
                    operation=operation_type,
                    expression=expression,
                    result=str(result)
                )

            
            return JsonResponse({
                'result': str(result),
                'error': None,
                'expression': expression
            })
            
        except ZeroDivisionError:
            return JsonResponse({
                'result': None,
                'error': 'Division by zero is not allowed'
            })
        except ValueError as e:
            return JsonResponse({
                'result': None,
                'error': 'Invalid mathematical operation'
            })
        except Exception as e:
            return JsonResponse({
                'result': None,
                'error': f'Error: {str(e)}'
            })
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required
def history_view(request):
    calculations = Calculation.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'calculations': calculations,
        'title': 'Calculation History'
    }
    return render(request, 'calculator/history.html', context)

@csrf_exempt
@login_required
def clear_history(request):
    if request.method == 'POST':
        Calculation.objects.filter(user=request.user).delete()
        return JsonResponse({'success': True, 'message': 'History cleared successfully'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

def about(request):
    context = {
        'title': 'About Calculator'
    }
    return render(request, 'calculator/about.html', context)


# Authentication Views
def register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('calculator:dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created successfully! Welcome {username}. Please log in.')
            return redirect('calculator:login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserRegistrationForm()
    
    context = {
        'form': form,
        'title': 'Register'
    }
    return render(request, 'calculator/register.html', context)


def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('calculator:dashboard')
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # Try to authenticate with username
            user = authenticate(request, username=username, password=password)
            
            # If not found, try with email
            if user is None:
                try:
                    user_obj = User.objects.get(email=username)
                    user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    user = None
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('calculator:dashboard')
            else:
                messages.error(request, 'Invalid username/email or password.')
    else:
        form = UserLoginForm()
    
    context = {
        'form': form,
        'title': 'Login'
    }
    return render(request, 'calculator/login.html', context)


def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('calculator:index')


@login_required(login_url='calculator:login')
def dashboard(request):
    """User dashboard with statistics"""
    user = request.user
    
    # Get user statistics
    total_calculations = Calculation.objects.filter(user=user).count()
    recent_calculations = Calculation.objects.filter(user=user).order_by('-created_at')[:10]
    
    # Get operation breakdown
    operations = Calculation.objects.filter(user=user).values('operation').distinct().count()
    
    context = {
        'title': 'Dashboard',
        'user': user,
        'total_calculations': total_calculations,
        'recent_calculations': recent_calculations,
        'operations_count': operations,
    }
    return render(request, 'calculator/dashboard.html', context)