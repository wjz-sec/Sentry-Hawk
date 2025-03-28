from django.http import JsonResponse
from django.views import View
from app.models import Asset_info, Projects


# 资产编辑视图
class editAsset(View):
    def post(self, request):
        res = {
            'code': 500,
            'msg': "编辑成功",
            'self': None,
        }

        data = request.data
        if not data.get('asset'):
            res['self'] = 'asset'
            res['msg'] = '资产不可为空'
            return JsonResponse(res)

        # 检查项目是否存在
        try:
            project_identifier = data.get('asset_project')
            if not project_identifier:
                res['self'] = 'asset_project'
                res['msg'] = '项目不能为空'
                return JsonResponse(res)

            # 尝试通过ID查找项目
            try:
                project_id = int(project_identifier)
                project = Projects.objects.filter(id=project_id).first()
            except (ValueError, TypeError):
                # 如果不是有效的ID，则通过名称查找
                project = Projects.objects.filter(name=project_identifier).first()

            if not project:
                res['self'] = 'asset_project'
                res['msg'] = f'项目 "{project_identifier}" 不存在'
                return JsonResponse(res)

            data['asset_project'] = project

        except Exception as e:
            res['self'] = 'asset_project'
            res['msg'] = f'查找项目时出错: {str(e)}'
            return JsonResponse(res)

        # 检查是否存在重复资产（排除当前正在编辑的资产）
        asset_id = data.get('id')
        duplicate_check = Asset_info.objects.filter(
            asset=data['asset'],
            asset_project=data['asset_project']
        )
        if asset_id:
            duplicate_check = duplicate_check.exclude(asset_id=asset_id)

        if duplicate_check.exists():
            res['self'] = 'asset'
            res['msg'] = '不可编辑为重复资产'
            return JsonResponse(res)

        try:
            if not asset_id:
                res['msg'] = '资产ID不能为空'
                return JsonResponse(res)

            # 获取原始资产数据
            try:
                # 打印接收到的所有数据
                print("接收到的数据:", data)
                
                # 直接通过资产名称查找
                asset_name = data.get('asset')
                project = data.get('asset_project')
                print(f"尝试查找资产: 名称={asset_name}, 项目={project}")
                
                # 先只用名称查找，看看是否存在
                all_assets = Asset_info.objects.filter(asset=asset_name)
                print(f"找到的所有匹配资产: {[(a.asset_id, a.asset, a.asset_project.name if a.asset_project else None) for a in all_assets]}")
                
                # # 然后再用项目过滤
                # original_asset = all_assets.filter(asset_project=project).first()
                
                # if not original_asset:
                #     if all_assets.exists():
                #         res['msg'] = f'找到同名资产，但不属于指定项目。\n当前资产所属项目: {[a.asset_project.name for a in all_assets]}'
                #     else:
                #         res['msg'] = f'未找到该资产。请确认:\n1. 资产名称 {asset_name} 是否正确\n2. 该资产是否属于正确的项目\n3. 该资产是否已被删除'
                #     return JsonResponse(res)

                # # 记录找到的资产信息
                # print(f"找到资产: ID={original_asset.asset_id}, 名称={original_asset.asset}, 项目={original_asset.asset_project.name if original_asset.asset_project else None}")
                # asset_id = original_asset.asset_id

            except Exception as e:
                print(f"查询出错: {str(e)}")
                res['msg'] = f"查询资产时出错: {str(e)}"
                return JsonResponse(res)

            # 构建更新字段
            update_fields = {}
            
            # 更新资产名称
            if data.get('asset'):
                update_fields['asset'] = data['asset']
            
            # 更新资产类型
            if data.get('asset_type'):
                update_fields['asset_type'] = data['asset_type']
            
            # 更新项目
            if data.get('asset_project'):
                update_fields['asset_project'] = data['asset_project']
            
            # 更新备注
            if data.get('asset_note') is not None:  # 允许清空备注
                update_fields['asset_note'] = data['asset_note']

            # 处理编辑时间格式
            if data.get('asset_editor_time'):
                try:
                    from datetime import datetime
                    # 将 "2024.11.25  09:02:42" 转换为 "2024-11-25 09:02:42"
                    date_str = data['asset_editor_time'].strip()
                    date_parts = date_str.split('  ')  # 注意这里是两个空格
                    if len(date_parts) == 2:
                        date_part = date_parts[0].replace('.', '-')
                        time_part = date_parts[1]
                        formatted_date = f"{date_part} {time_part}"
                        # 验证日期格式
                        datetime.strptime(formatted_date, '%Y-%m-%d %H:%M:%S')
                        update_fields['asset_editor_time'] = formatted_date
                except Exception as e:
                    res['msg'] = '日期格式错误，请使用格式: YYYY.MM.DD HH:MM:SS'
                    return JsonResponse(res)

            # 只有在有字段更新时才执行更新操作
            if update_fields:
                Asset_info.objects.filter(asset_id=asset_id).update(**update_fields)
                res['code'] = 200
                res['msg'] = "更新成功"
            else:
                res['msg'] = "没有需要更新的字段"

        except Asset_info.DoesNotExist:
            res['msg'] = f'找不到ID为 {asset_id} 的资产'
        except Exception as e:
            res['msg'] = f'更新资产时出错: {str(e)}'

        return JsonResponse(res, safe=False, json_dumps_params={'ensure_ascii': False})
