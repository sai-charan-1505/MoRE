const API_BASE = "http://127.0.0.1:8000"

async function requestRecommendation(payload){
const res = await fetch(`${API_BASE}/recommend`,{
method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify(payload)
})
return await res.json()
}
