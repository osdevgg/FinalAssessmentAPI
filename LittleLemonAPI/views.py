from django.shortcuts import render,  get_object_or_404

from .models import Category, MenuItem, Cart, Order, OrderItem
from django.contrib.auth.models import User, Group

from rest_framework import viewsets, status

from rest_framework.response import Response

from .serializers import CategorySerializer, MenuItemSerializer, CartSerializer, OrderSerializer, GroupSerializer, UserSerializer

from rest_framework.permissions import IsAuthenticated, IsAdminUser, BasePermission

#from rest_framework.filters import DjangoFilterBackend
from django_filters.rest_framework import DjangoFilterBackend

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


class CategoryViewSet(viewsets.ModelViewSet):
	queryset = Category.objects.all()
	serializer_class = CategorySerializer

	def get_permissions(self):
		permission_classes = [IsAuthenticated]
		if self.request.method in ( 'POST', 'PUT', 'PATCH', 'DELETE' ):
			permission_classes = [ IsManager, IsAdminUser ]
		return [permission() for permission in permission_classes]

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


class CartViewSet(viewsets.ViewSet):
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
#		return Response({"message":"All carts"}, status.HTTP_200_OK)

	def create(self, request, *args, **kwargs):
		user = self.request.user.id
		username = self.request.user.username
		menuitem = self.request.data['menuitem']
		quantity = self.request.data['quantity']
		unit_price = MenuItem.objects.get(id = menuitem).price
		price = unit_price * quantity
		cart_serialized  = CartSerializer(data = { 'user': user, 'menuitem': menuitem, 'quantity': quantity, 'unit_price': unit_price, 'price': price })
		##         cart_serialized = CartSerializer(data = request.data)
		cart_serialized.is_valid(raise_exception=True)
		cart_serialized.save()  
		return Response( "Added " + quantity + " " + menuitem + " to " + username + " cart ", status.HTTP_201_CREATED)
#		return Response(cart_serialized.data, status.HTTP_201_CREATED)

	def destroy(self, request, pk=None):
		return Response({"message":"Deleting a cart"}, status.HTTP_200_OK)


class OrderViewSet(viewsets.ModelViewSet):
	queryset = Order.objects.all()
	serializer_class = OrderSerializer


	def list(self, request):
		return Response({"message":"All orders"}, status.HTTP_200_OK)
	def create(self, request):
		return Response({"message":"Creating a order"}, status.HTTP_201_CREATED)
	def update(self, request, pk=None):
		return Response({"message":"Updating a order"}, status.HTTP_200_OK)
	def retrieve(self, request, pk=None):
		return Response({"message":"Displaying a order"}, status.HTTP_200_OK)
	def partial_update(self, request, pk=None):
		return Response({"message":"Partially updating a order"}, status.HTTP_200_OK)
	def destroy(self, request, pk=None):
		return Response({"message":"Deleting a order"}, status.HTTP_200_OK)


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
			deliverygroup.user_set.add(user)
			return Response("User " + user.username + " added to Delivery crew group", status.HTTP_201_CREATED)

#    def delete(self, request, pk):
	def destroy(self, request, pk):
		deliverygroup = Group.objects.get(name="Delivery crew")
		if pk:
			user = get_object_or_404(User, id = pk)
#TODO: test if user belongs to said group			
			deliverygroup.user_set.remove(user)
			return Response("User " + user.username + " removed from Delivery crew group", status.HTTP_200_OK)


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

