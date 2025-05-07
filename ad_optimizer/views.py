from django.shortcuts import render
from django.http import JsonResponse
import pandas as pd
from scipy.optimize import linprog
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import User, AdCampaign, AdPerformance
from .serializers import UserSerializer, AdCampaignSerializer, AdPerformanceSerializer
import logging

logger = logging.getLogger(__name__)


class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class AdCampaignListCreateView(generics.ListCreateAPIView):
    queryset = AdCampaign.objects.all()
    serializer_class = AdCampaignSerializer

class AdPerformanceListView(generics.ListAPIView):
    queryset = AdPerformance.objects.all()
    serializer_class = AdPerformanceSerializer


class OptimizeBudgetAPI(APIView):
    def get(self, request):
        # Example response
        return Response({"message": "Optimize budget API is working!"})
    
    def post(self, request):
        try:
            # Parse the request data
            data = request.data
            logger.debug(f"Request data: {data}")
            total_budget = float(data.get('budget'))
            industry = data.get('industry')

            # Validate inputs
            if not total_budget or total_budget < 1000:
                logger.error("Budget validation failed.")
                return Response({"error": "Budget must be at least 1000."}, status=status.HTTP_400_BAD_REQUEST)
            if not industry:
                logger.error("Industry validation failed.")
                return Response({"error": "Industry is required."}, status=status.HTTP_400_BAD_REQUEST)

            # Load the ad platform data
            try:
                df = pd.read_csv('ad_data.csv')
                logger.debug(f"Loaded data: {df.head()}")
            except FileNotFoundError:
                logger.error("ad_data.csv not found.")
                return Response({"error": "ad_data.csv not found."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Validate required columns
            required_columns = ['platform', 'budget', 'reach', 'cost_per_click', industry]
            for col in required_columns:
                if col not in df.columns:
                    logger.error(f"Missing required column: {col}")
                    return Response({"error": f"Missing required column '{col}' in dataset."}, status=status.HTTP_400_BAD_REQUEST)

            # Validate data integrity
            if (df['budget'] <= 0).any():
                logger.error("Zero or negative budgets found in dataset.")
                return Response({"error": "Zero or negative budgets found in dataset."}, status=status.HTTP_400_BAD_REQUEST)
            if (df['reach'] <= 0).any():
                logger.error("Zero or negative reach values found in dataset.")
                return Response({"error": "Zero or negative reach values found in dataset."}, status=status.HTTP_400_BAD_REQUEST)
            if (df['cost_per_click'] <= 0).any():
                logger.error("Zero or negative cost_per_click values found in dataset.")
                return Response({"error": "Zero or negative cost_per_click values found in dataset."}, status=status.HTTP_400_BAD_REQUEST)

            # Calculate adjusted reach
            if industry not in df.columns:
                logger.error(f"Industry column '{industry}' not found in dataset.")
                return Response({"error": f"Industry column '{industry}' not found in dataset."}, status=status.HTTP_400_BAD_REQUEST)
            df['adjusted_reach'] = df['reach'] * df[industry]
            logger.debug(f"Adjusted reach calculated: {df[['platform', 'adjusted_reach']]}")

            if (df['adjusted_reach'] <= 0).any():
                logger.error("Adjusted reach contains invalid values.")
                return Response({"error": "Adjusted reach contains invalid values. Please check the dataset."}, status=status.HTTP_400_BAD_REQUEST)

            # Linear programming setup
            reach_per_rupee = df['adjusted_reach'] / df['budget']  # Reach per unit budget
            c = -reach_per_rupee.values  # Negate for maximization
            A_eq = [[1] * len(df)]  # Total budget constraint
            b_eq = [total_budget]
            bounds = [(0.1 * total_budget, 0.5 * total_budget) for _ in range(len(df))]  # Bounds for each platform

            # Solve the linear programming problem
            result = linprog(c=c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')

            # Check if the optimization was successful
            if not result.success:
                logger.error("Linear programming optimization failed.")
                return Response({"error": "Optimization failed. Please revise constraints."}, status=status.HTTP_400_BAD_REQUEST)

            # Allocate the optimized budget
            df['allocated_budget'] = result.x
            df['estimated_reach'] = df['adjusted_reach'] * (df['allocated_budget'] / df['budget'])
            df['estimated_ads'] = df['allocated_budget'] / df['cost_per_click']

            # Construct the response
            response = {
                "total_budget": total_budget,
                "total_estimated_reach": int(df['estimated_reach'].sum()),
                "platform_allocations": {
                    row['platform']: {
                        "allocated_budget": int(row['allocated_budget']),  # Ensure budget is rounded to an integer
                        "estimated_reach": int(row['estimated_reach']),
                        "estimated_ads": int(row['allocated_budget'] / row['cost_per_click'])  # Ensure ads are rounded to an integer
                    }
                    for _, row in df.iterrows()
                }
            }
            logger.debug(f"Response data: {response}")
            return Response(response, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error in optimization: {str(e)}", exc_info=True)
            return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
