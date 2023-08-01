from django.shortcuts import render,  get_object_or_404

from .models import Category, MenuItem, Cart, Order, OrderItem
from django.contrib.auth.models import User, Group

from rest_framework import viewsets, status

from rest_framework.response import Response

from .serializers import CategorySerializer, MenuItemSerializer, CartSerializer, OrderSerializer, OrderItemSerializer, GroupSerializer, UserSerializer

from rest_framework.permissions import IsAuthenticated, IsAdminUser, BasePermission

#from rest_framework.filters import DjangoFilterBackend
from django_filters.rest_framework import DjangoFilterBackend

from django.utils import timezone

from rest_framework import request

# Create your views here.

#
#  PERMISSIONS
#
        

class IsManager(BasePermission):
    def has_permission(self, request, view):
        # Check if the user belongs to the Manager group
        return (request.user and request.user.is_authenticated and request.user.groups.filter(name='Manager').exists()) or\
                    request.user.is_superuser

class IsDeliveryCrew(BasePermission):
    def has_permission(self, request, view):
        # Check if the user belongs to the Delivery crew group
        return request.user and request.user.is_authenticated and request.user.groups.filter(name='Delivery crew').exists()
#        return request.user.groups.filter(name='Delivery crew').exists()

class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        # Check if the user is a Customer according to app definitions
#        return request.user.groups.filter(name='Delivery crew').exists()
#        return request.user and request.user.is_authenticated and \
        return request.user.is_authenticated and \
                    ( not request.user.groups.filter(name='Delivery crew').exists() ) and \
                    ( not request.user.groups.filter(name='Manager').exists() ) and \
                    ( not request.user.is_superuser )

#
# GROUPS - MANAGER
#

class ManagerViewSet(viewsets.ViewSet):
	queryset = User.objects.all()
	serializer_class = UserSerializer
	permission_classes = [ IsAdminUser ]
	
	def list(self, request):
		managergroup = Group.objects.get(name="Manager")
		managers = managergroup.user_set.all()
		serializer = UserSerializer(managers, many=True)
		return Response(serializer.data, status.HTTP_200_OK)


	def create(self, request):
		username = request.data['username']
		if username:
			managergroup = Group.objects.get(name="Manager")
			user = get_object_or_404(User, username = username)
			managergroup.user_set.add(user)
			return Response("User " + user.username + " added to Managers group", status.HTTP_201_CREATED)


	def destroy(self, request, pk=None):
#TODO: test if user belongs to said group		
		managergroup = Group.objects.get(name="Manager")
		if pk:
			user = get_object_or_404(User, id = pk)
			managergroup.user_set.remove(user)
			return Response("User " + user.username + " removed from Managers group", status.HTTP_200_OK)

#
# GROUPS - DELIVERY CREW
#


class DeliveryCrewViewSet(viewsets.ViewSet):
	queryset = User.objects.all()
	serializer_class = UserSerializer
	permission_classes = [IsManager]
    
#    queryset = deliverygroup.objects.get(name = 'Delivery crew')
    
#    queryset = Group.objects.get(name='Delivery crew').user_set.all()
#    queryset = User.objects.all('Delivery Crew')

	def list(self, request):
		deliverygroup = Group.objects.get(name="Delivery crew")
		delivery = deliverygroup.user_set.all()
		serializer = UserSerializer(delivery, many=True)
		return Response(serializer.data)
#	    # delivery = queryset.user_set.all()
#	    #deliverygroup = Group.objects.get(name = 'Delivery crew')
#		deliverycrewgroup = Group.objects.get(name = 'Delivery crew').user_set.all()
#		user = get_object_or_404(User, )
#		serializer = self.get_serializer(deliverycrewgroup, many = True)
#		#UserSerializer(delivery, many=True)
#		return Response(serializer.data, status.HTTP_200_OK)
    
#    def create(self,request, *args, **kwargs):
	def create(self,request, *args, **kwargs):
#		deliverygroup = Group.objects.get(name = 'Delivery crew')
#		username = request.data.get('username')
#		user = get_object_or_404(User, username = username)
#		deliverygroup.user_set.add(user)
#		return Response("User " + user.username + " added to Delivery crew group", status.HTTP_201_CREATED)
		username = request.data['username']
		if username:
			deliverygroup = Group.objects.get(name="Delivery crew")
			user = get_object_or_404(User, username = username)
#TODO: test if user already belongs to said group
			deliverygroup.user_set.add(user)
			return Response("User " + user.username + " added to Delivery crew group", status.HTTP_201_CREATED)

#    def delete(self, request, pk):
	def destroy(self, request, pk):
		deliverygroup = Group.objects.get(name="Delivery crew")
		if pk:
			user = get_object_or_404(User, id = pk)
#TODO: test if user belongs to said group before trying to remove them		
			deliverygroup.user_set.remove(user)
			return Response("User " + user.username + " removed from Delivery crew group", status.HTTP_200_OK)

#
# MENU - CATEGORY
#

class CategoryViewSet(viewsets.ModelViewSet):
	queryset = Category.objects.all()
	serializer_class = CategorySerializer

	def get_permissions(self):
		permission_classes = [IsAuthenticated]
		if self.request.method in ( 'POST', 'PUT', 'PATCH', 'DELETE' ):
#			permission_classes = [ IsManager, IsAdminUser ]
			permission_classes = [ IsAdminUser ]
		return [permission() for permission in permission_classes]

#
# MENU - MENUITEM
#

class MenuItemViewSet(viewsets.ModelViewSet):
	queryset = MenuItem.objects.all()
	serializer_class = MenuItemSerializer
	filter_backends = [DjangoFilterBackend]
	filterset_fields = ['category__title', 'price', 'featured']
	ordering_fields=['price','category','featured']
	search_fields=['category__title','featured']

	def get_permissions(self):
		permission_classes = [IsAuthenticated]
		if self.request.method in ( 'POST', 'PUT', 'PATCH', 'DELETE' ):
			permission_classes = [ IsManager, IsAdminUser ]
		return [permission() for permission in permission_classes]

#
# CART
#

class CartViewSet(viewsets.ViewSet):
	permission_classes = [ IsCustomer ]
	queryset = Cart.objects.all()
	serializer_class = CartSerializer

	def list(self, request):
		queryset = Cart.objects.all()
		serializer_class = CartSerializer
		permission_classes = [ IsCustomer ]

#		def get_queryset(self):
#			return Cart.objects.filter(user=self.request.user)
		menuitems = Cart.objects.filter(user=self.request.user)
		serializer = CartSerializer(menuitems, many=True)
		return Response(serializer.data, status.HTTP_200_OK)


	def create(self, request, *args, **kwargs):
		serializer = CartSerializer(data = request.data)
		if serializer.is_valid():
			serializer.validated_data['user'] = self.request.user
			menuitem_instance = serializer.validated_data['menuitem']
			serializer.validated_data['unit_price'] = MenuItem.objects.get(id = menuitem_instance.id ).price
			serializer.validated_data['price'] = serializer.validated_data['quantity'] * serializer.validated_data['unit_price']
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)		
		
	def destroy(self, request, pk=None):
		return Response({"message":"Deleting a cart"}, status.HTTP_200_OK)

#
# ORDER
#

class OrderViewSet(viewsets.ModelViewSet):
	queryset = Order.objects.all()
	serializer_class = OrderSerializer
#	user = self.request.user

	def get_queryset(self, request):
		user = self.request.user
		queryset = Order.objects.none()
		if request.user.groups.filter(name='Manager').exists():
			queryset = Order.objects.all()
		elif request.user.groups.filter(name='Delivery crew').exists():
			queryset = Order.objects.filter(delivery_crew = user)
		elif request.user.IsAuthenticated:
			queryset = Order.objects.filter(user = user)
		return queryset
	

	def list(self, request):
		permission_classes = [ IsManager, IsDeliveryCrew, IsCustomer ]
		data = self.request.data
		serializer = OrderSerializer(data = data, many=True)
		serializer.is_valid()
		return Response(serializer.data, status.HTTP_200_OK)

		return Response({"message":"All orders"}, status.HTTP_200_OK)
	def create(self, request, *args, **kwargs):

		permission_classes = [ IsCustomer, ]
		serializer_class = OrderItemSerializer
		queryset = OrderItem.objects.all()

		user = self.request.user
		order = Order.objects.create(
			user = user,
		    delivery_crew = None,
		    status = 0,
		    total = 0,
		    date = timezone.now()	
			)
		

# Fetch items 
		items_response = self._get_items(user)

		for item_data in items_response:
			item_serializer = MenuItemSerializer( data = item_data )
			item_serializer.validated_data['user'] = order.id
			if item_serializer.is_valid():
				item_instance = item_serializer.save()
				OrderItem.objects.create( item = item_instance )
			else: 
				return Response(item_serializer.errors, status.HTTP_409_CONFLICT)
		return Response({"message": "Cart items added to OrderItem table"})
#		cart = Cart.objects.get(user = user)
#		order = Order.objects.create(user = user)
#		if cart:
#			for item in cart.iterator:
#				OrderItem.object.create(
#					    order = Order.id,
#						menuitem = item.menuitem,
#						quantity = item.quantity
#						unit_price = item.unit_price
#						price = item.price
#				)

	def _get_items(self, *args, **kwargs):
		items_url = "/api/cart/menu-items"  
		# Replace this with the actual URL for the ItemListView
		response = request.GET(items_url)
		return response.data


		return Response({"message":"Creating a order"}, status.HTTP_201_CREATED)
	def update(self, request, pk=None):
		return Response({"message":"Updating a order"}, status.HTTP_200_OK)
	def retrieve(self, request, pk=None):
		return Response({"message":"Displaying a order"}, status.HTTP_200_OK)
	def partial_update(self, request, pk=None):
		return Response({"message":"Partially updating a order"}, status.HTTP_200_OK)
	def destroy(self, request, pk=None):
		return Response({"message":"Deleting a order"}, status.HTTP_200_OK)




class BookViewSet(viewsets.ViewSet):

	def list(self, request):
		return Response({"message":"All books"}, status.HTTP_200_OK)
	def create(self, request):
		return Response({"message":"Creating a book"}, status.HTTP_201_CREATED)
	def update(self, request, pk=None):
		return Response({"message":"Updating a book"}, status.HTTP_200_OK)
	def retrieve(self, request, pk=None):
		return Response({"message":"Displaying a book"}, status.HTTP_200_OK)
	def partial_update(self, request, pk=None):
		return Response({"message":"Partially updating a book"}, status.HTTP_200_OK)
	def destroy(self, request, pk=None):
		return Response({"message":"Deleting a book"}, status.HTTP_200_OK)

