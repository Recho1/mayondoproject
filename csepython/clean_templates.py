import os
import re

templates_dir = "home/templates"

# List of templates to completely replace with simple versions
simple_templates = {
    "allsales.html": """{% extends "base.html" %}
{% load static %}

{% block content %}
<div class="container mx-auto px-4 py-8">
    <h1 class="text-2xl font-bold mb-4">All Sales</h1>
    <div class="bg-white rounded-lg shadow overflow-hidden">
        <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
                <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Customer</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Product</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Quantity</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
                {% for sale in sales %}
                <tr>
                    <td class="px-6 py-4">{{ sale.customername }}</td>
                    <td class="px-6 py-4">{{ sale.productname.productname }}</td>
                    <td class="px-6 py-4">{{ sale.quantity }}</td>
                    <td class="px-6 py-4">${{ sale.totalprice }}</td>
                    <td class="px-6 py-4">
                        <a href="{% url 'view_sale' sale.id %}" class="text-blue-600 hover:text-blue-900">View</a>
                        <a href="{% url 'update_sale' sale.id %}" class="text-green-600 hover:text-green-900 ml-2">Edit</a>
                    </td>
                </tr>
                {% empty %}
                <tr><td colspan="5" class="px-6 py-4 text-center text-gray-500">No sales found</td></tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    <div class="mt-4">
        <a href="{% url 'dashboard' %}" class="bg-gray-500 text-white px-4 py-2 rounded">Back to Dashboard</a>
    </div>
</div>
{% endblock %}""",
    
    "allusers.html": """{% extends "base.html" %}
{% load static %}

{% block content %}
<div class="container mx-auto px-4 py-8">
    <h1 class="text-2xl font-bold mb-4">All Users</h1>
    <div class="bg-white rounded-lg shadow overflow-hidden">
        <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
                <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Username</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Role</th>
                </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
                {% for user in users %}
                <tr>
                    <td class="px-6 py-4">{{ user.username }}</td>
                    <td class="px-6 py-4">{{ user.email }}</td>
                    <td class="px-6 py-4">{{ user.profile.role }}</td>
                </tr>
                {% empty %}
                <tr><td colspan="3" class="px-6 py-4 text-center text-gray-500">No users found</td></tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    <div class="mt-4">
        <a href="{% url 'dashboard' %}" class="bg-gray-500 text-white px-4 py-2 rounded">Back to Dashboard</a>
    </div>
</div>
{% endblock %}""",
    
    "dashboard.html": """{% extends "base.html" %}
{% load static %}

{% block content %}
<div class="text-center">
    <h1 class="text-3xl font-bold text-gray-900 mb-4">Dashboard</h1>
    <p class="text-xl text-gray-600 mb-8">Welcome back, {{ user.username }}!</p>
    
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
        <div class="bg-blue-100 p-6 rounded-lg shadow">
            <h3 class="text-lg font-semibold text-blue-800">Total Stock</h3>
            <p class="text-3xl font-bold text-blue-600">{{ total_stock|default:"0" }}</p>
        </div>
        <div class="bg-green-100 p-6 rounded-lg shadow">
            <h3 class="text-lg font-semibold text-green-800">Total Sales</h3>
            <p class="text-3xl font-bold text-green-600">{{ total_sales|default:"0" }}</p>
        </div>
        <div class="bg-purple-100 p-6 rounded-lg shadow">
            <h3 class="text-lg font-semibold text-purple-800">Total Users</h3>
            <p class="text-3xl font-bold text-purple-600">{{ total_users|default:"0" }}</p>
        </div>
    </div>
    
    <div class="mt-8 grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl mx-auto">
        <a href="{% url 'stock' %}" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">Manage Stock</a>
        <a href="{% url 'sales' %}" class="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded">Manage Sales</a>
        <a href="{% url 'allstock' %}" class="bg-indigo-500 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded">View All Stock</a>
        <a href="{% url 'allsales' %}" class="bg-purple-500 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded">View All Sales</a>
    </div>
    
    <div class="mt-8">
        <a href="{% url 'logout' %}" class="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded">Logout</a>
    </div>
</div>
{% endblock %}""",
}

# Replace problematic templates
for filename, content in simple_templates.items():
    filepath = os.path.join(templates_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Replaced: {filename}")

print("🎉 All templates fixed!")
