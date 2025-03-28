from django.urls import path
from api.views.asset import addAsset, editAsset, deleteAsset, getAssetType, getAssetProject, downloadAsset, batchAddAsset, assetDetail
from api.views.asset.getCount import get_asset_counts, getSensitiveCounts

urlpatterns = [
    path('add/', addAsset.addAsset.as_view()),  # 新增资产
    path('edit/', editAsset.editAsset.as_view()),  # 编辑资产
    path('delete/', deleteAsset.deleteAsset.as_view()),  # 删除资产
    path('type/', getAssetType.getAssetType.as_view()),  # 获取资产类型
    path('project/', getAssetProject.getAssetProject.as_view()),  # 获取资产类型
    path('downloadAssetInfo/', downloadAsset.downloadAssetInfo.as_view()),  # 导出用户资产类型
    path('BatchAdd/', batchAddAsset.BatchAddAsset.as_view()),  # 导入用户资产类型

    path('detail/', assetDetail.AssetDetail.as_view()),  # 资产详情数据获取
    path('count/', get_asset_counts),  # 添加新的路由规则

    path('counts/', getSensitiveCounts)
]