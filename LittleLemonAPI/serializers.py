from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import MenuItem, Category, Order, Cart, OrderItem

from django.contrib.auth.models import User, Group 

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model =  Group
        fields = [ 'id', 'name', ]

class UserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True, read_only=True)

    class Meta():
        model = User
#        fields = '__all__'
        fields = [ 'id', 'username', 'email', 'groups' ]

class MenuItemSerializer(serializers.ModelSerializer):
#    category = serializers.StringRelatedField(write_only=True)
    class Meta:
        model = MenuItem
#        fields = '__all__'
        fields = ['title', 'price', 'featured', 'category',]
#        fields = ['title', 'price', 'featured']
#        extra_kwargs = {
#            'price': {'min_value': 1,},
#            'category': {'required': True,}, 
#            'title': {'validators':[UniqueValidator(queryset=MenuItem.objects.all())]},
#        }

class CategorySerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer(many=True, read_only=True)
    class Meta:
        model = Category
        fields = '__all__'
#        fields = ['title', 'slug', 'menuitem']

class CartSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cart
        fields = '__all__'

    def create(self, validated_data):
        menuitem_instance = validated_data['menuitem']
        validated_data['unit_price'] = menuitem_instance.price
        # Perform dependency handling and set dependent attributes
        price = validated_data['quantity'] * validated_data['unit_price']
        validated_data['price'] = price  # Set the dependent attribute
        return super().create(validated_data)
    
class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = '__all__'




