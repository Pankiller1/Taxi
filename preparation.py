import pandas as pd
import os


data_folder = "shenzhen/taxi"

date_range = [date.strftime("%Y-%m-%d").lstrip("0").replace("-0", "-") for date in pd.date_range("2018-10-01", "2018-10-30", freq="D")]

results = []

for file_date in date_range:
    file_path = os.path.join(data_folder, f"{file_date}.csv")

    if not os.path.exists(file_path):
        print(f"File not found:{file_path}")
        continue

    data = pd.read_csv(file_path)
    data['time'] = pd.to_datetime(file_date + " " +data['time'], format='%Y-%m-%d %H:%M:%S')

    # 按车辆分组
    grouped = data.groupby('VehicleNum')
    
    # 存储单日结果的列表
    daily_results = []
    
    # 遍历每个车辆组
    for vehicle, group in grouped:
        group = group.reset_index(drop=True)
        start_idx = None
        
        # 遍历每辆车的数据
        for i in range(len(group)):
            # 检查状态变化
            if group.loc[i, 'status'] == 1 and start_idx is None:
                # 记录新的起点
                start_idx = i
            elif group.loc[i, 'status'] == 0 and start_idx is not None:
                # 记录终点并保存该段轨迹
                trajectory = group.loc[start_idx:i, ['longitude', 'latitude']].values.tolist()
                start_time = group.loc[start_idx, 'time']
                end_time = group.loc[i, 'time']
                time_elapsed = (end_time - start_time).total_seconds()
                
                if time_elapsed >= 180 and time_elapsed <= 7200:
                    # 保存结果
                    daily_results.append({
                        "VehicleNum": vehicle,
                        "trajectory": trajectory,
                        "start_time": start_time,
                        "end_time": end_time,
                        "time_elapsed": time_elapsed
                    })
                
                # 重置起点
                start_idx = None
    results.extend(daily_results)
    print(f"Finished processing {file_date}")

results_df = pd.DataFrame(results)
results_df.to_csv("results.csv", index=False, encoding='utf-8')

print("finished to csv")