import pandas as pd
import os


data_folder = "../data"
feature = ['Lng', 'Lat', 'Hour', "traffic"]

results = []

for filename in os.listdir(data_folder):
    if filename.endswith("traffic_average.csv"):

        file_path = os.path.join(data_folder, filename)
        data = pd.read_csv(file_path)
        
        data['Time'] = pd.to_datetime(data['Time'], format='%Y/%m/%d %H:%M:%S')

        # 按车辆分组
        grouped = data.groupby('VehicleNum')
        # 存储单日结果的列表
        daily_results = []
        for vehicle, group in grouped:
            group = group.reset_index(drop=True)
            start_idx = None

            for i in range(len(group)):
                if group.loc[i, 'Status'] == 1 and start_idx is None:
                    start_idx = i
                elif group.loc[i, 'Status'] == 0 and start_idx is not None:
                    trajectory = group.loc[start_idx:i, feature].values.tolist()
                    start_time = group.loc[start_idx, 'Time']
                    end_time = group.loc[i, 'Time']
                    time_elapsed = (end_time - start_time).total_seconds()
                    if time_elapsed >= 600 and time_elapsed <= 3000:
                        daily_results.append({
                            "VehicleNum": vehicle,
                            "trajectory": trajectory,
                            "start_time": start_time,
                            "end_time": end_time,
                            "time_elapsed": time_elapsed
                        })

                    start_idx = None
        results.extend(daily_results)
        print(f"Finished processing {filename}")

results_df = pd.DataFrame(results)
results_df.to_csv(f"../data/results_chengdu_{len(feature)}d.csv", index=False, encoding='utf-8')

print("finished to csv")