features = np.array([]) # to hold the feature array, must first be loaded

for row in features.T:
    decomp_row = seasonal_decompose(row,freq=52,extrapolate_trend='freq')
    norm1 = decomp_row.seasonal
    norm2 = decomp_row.resid
    norm3 = decomp_row.trend
    signal = np.vstack((norm1,norm2))
    signal = np.vstack((signal,norm3))
    buf = np.vstack((buf,signal)) if np.size(buf) else signal
count = 0
for year in range(2010,2020):
    for week in range(1,53):
        np.save(os.path.join(dataset_dir,str(year),str(week),'Decomposed_keywords'),buf.T[count])
        count+=1    