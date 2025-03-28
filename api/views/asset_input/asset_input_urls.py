from django.urls import path
from api.views.asset_input import asset_input_addAsset,asset_input_editAsset,asset_input_downloadAsset,asset_input_batchAddAsset,asset_input_deleAsset_input


urlpatterns = [
    path('add/', asset_input_addAsset.addAsset.as_view()),  # 新增资产
    path('edit/', asset_input_editAsset.editAsset.as_view()),  # 编辑资产
    path('delete/', asset_input_deleAsset_input.deleteAsset.as_view()),  # 删除资产
    #path('delete/', deleteAsset.deleteAsset.as_view()),
    path('downloadAssetInfo/', asset_input_downloadAsset.downloadAssetInfo.as_view()),  # 导出用户资产类型
    path('BatchAdd/', asset_input_batchAddAsset.BatchAddAsset.as_view()),  # 导入用户资产类型

]