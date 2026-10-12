from django.shortcuts import render , get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView 
from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions
from products.serializers import ProductSerializer , CategorySerializer
from products.models import Product , Category
from rest_framework import status


class ProductView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = ProductSerializer

    def get(self , request):
            products = Product.objects.all()
            serializer = ProductSerializer(products , many = True)
            return Response(serializer.data)
    
    def post(self, request ,id):

       serializer = ProductSerializer(data=request.data)

       if serializer.is_valid():
           product = serializer.save(owner=request.user)

           return Response(
             ProductSerializer(product).data,
             status=status.HTTP_201_CREATED
          )

       return Response(
         serializer.errors,
         status=status.HTTP_400_BAD_REQUEST
       )

    def patch(self , request, id):
         if not request.user.is_authenticated:
              return Response(
                   {"error":"Authentication is required"},
                   status=status.HTTP_401_UNAUTHORIZED
              )

         if request.user.role == "customer":
              return Response(
                   {"error":"U r not allowed to chnge."},
                   status=status.HTTP_400_BAD_REQUEST
              )
         
         product = get_object_or_404(Product , id=id)

         is_owner = product.owner == request.user
         is_admin = request.user.is_staff

         if not (is_owner or is_admin):
              return Response(
                   {"error":"U can only edit ur own product"},
                   status=status.HTTP_403_FORBIDDEN
              )
         
         serializer = ProductSerializer(product , data=request.data, partial=True)
         if serializer.is_valid():
              serializer.save()
              return Response({"message":"Updated successfully"},status=status.HTTP_200_OK)
         else:
              return Response({"error":"Something went wrong"},status=status.HTTP_400_BAD_REQUEST)
         
    def delete(self , request, id):
         if not request.user.is_authenticated:
              return Response({"error":"Authorization is required"},
                               status=status.HTTP_401_UNAUTHORIZED 
                               )
         
         product = Product.objects.get(id=id)

         is_owner = request.user == product.owner
         is_admin = request.user.is_staff

         if not (is_owner or is_admin):
              return Response({"error":"u can only delete ur own  product"},status=status.HTTP_403_FORBIDDEN)
         
         product.delete()
         return Response({"message":"Successfully Deleted."},status=status.HTTP_204_NO_CONTENT)

class CategoryView(APIView): 
     permission_classes = [permissions.IsAuthenticatedOrReadOnly]
     serializer_class = CategorySerializer

     def get(self , request):
          category = Category.objects.all()
          serializer = CategorySerializer(category , many=True)
          return Response(serializer.data)

     def post(self,request,id):
          
          if request.user.role == "customer":
               return Response({"error":"U r not allowed to add category."})

          if not Category.objects.filter(
               category_name=request.data.get("category_name")
               ).exists():
               serializer = CategorySerializer(data=request.data)
               
               if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=201)

               return Response(serializer.errors, status=400)

          return Response(
               {"error": "Category already exists"},
               status=400
               )
     def delete(self , request,id):
          if not request.user.is_authenticated:
               return Response({"error":"Authentication is required."},status=status.HTTP_401_UNAUTHORIZED)

          

          if not request.user.is_staff:
               return Response({"error":"U r not allowed to change the category."},status=status.HTTP_400_BAD_REQUEST)

          category = Category.objects.get(id=id)  

        
          category.delete()   

          return Response({"message":"Category Successfully Deleted."},status=status.HTTP_200_OK)
               