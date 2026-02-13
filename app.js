const btn = document.getElementById("recommendBtn")
const resultsBox = document.getElementById("results")

btn.addEventListener("click", async () => {

const payload = {
age: Number(document.getElementById("age").value),
gender: document.getElementById("gender").value,
relationship_status: document.getElementById("relationship_status").value,
mood: document.getElementById("mood").value,
time_of_day: document.getElementById("time_of_day").value,
month: Number(document.getElementById("month").value),
watch_with: document.getElementById("watch_with").value,
weather: document.getElementById("weather").value,
top_n: 5
}

resultsBox.innerHTML = ""

const data = await requestRecommendation(payload)

if(!data || !data.recommended_movies){
resultsBox.innerHTML = "<div class='movie-card'><div class='movie-title'>No results</div></div>"
return
}

data.recommended_movies.forEach(item=>{
const card = document.createElement("div")
card.className = "movie-card"

const title = document.createElement("div")
title.className = "movie-title"
title.textContent = item.movie_title

const score = document.createElement("div")
score.className = "score"
score.textContent = (item.score*100).toFixed(1)+"%"

card.appendChild(title)
card.appendChild(score)

resultsBox.appendChild(card)
})

})
