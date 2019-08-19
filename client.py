from Breaches import Breaches

b = Breaches(modelDays=2500, predictDays=None,
             dataSource=Breaches.getEnv("DATA_SOURCE"),
             apiKey=Breaches.getEnv("ALPHA_VANTAGE_API_KEY"))

b.open(path="breaches.json", forceRemote=False)

for i in b.IDs:
    b.predict(i)

b.showMeta()

for i in b.IDs:
    b.plot(i)
