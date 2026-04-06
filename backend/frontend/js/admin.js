const API = window.location.origin

function abrirWhats(url){
  window.open(url, "_blank")
}

function formatarTelefone(num){
  if(!num) return "5551999999999"

  num = num.replace(/\D/g, "")

  if(num.startsWith("55")){
    return num
  }

  if(num.startsWith("0")){
    num = num.substring(1)
  }

  return "55" + num
}

function carregarAgenda(){

fetch(`${API}/agendamentos`)
.then(res => res.json())
.then(lista => {

const container = document.getElementById("lista")
container.innerHTML = ""

mostrarProximo(lista)

lista.forEach(a => {

const statusClass = a.status === "finalizado" ? "finalizado" : "pendente"

const item = document.createElement("div")
item.className = "card-agendamento " + statusClass

// 📲 mensagem
const mensagem = 
`Olá ${a.nome}! 💈\n\n` +
`Lembrando do seu horário:\n\n` +
`📅 ${a.data}\n` +
`⏰ ${a.horario}\n\n` +
`Barbearia Yagors Barber`

const telefone = formatarTelefone(a.telefone)
const urlWhats = `https://wa.me/${telefone}?text=${encodeURIComponent(mensagem)}`

// botões
const btnAvisar = document.createElement("button")
btnAvisar.innerText = "📲 Avisar"
btnAvisar.onclick = () => abrirWhats(urlWhats)

const btnFinalizar = document.createElement("button")
btnFinalizar.innerText = "✅ Finalizar"
btnFinalizar.onclick = () => finalizar(a.nome, a.data, a.horario)

const btnCancelar = document.createElement("button")
btnCancelar.innerText = "❌ Cancelar"
btnCancelar.onclick = () => cancelar(a.nome, a.data, a.horario)

// HTML base
item.innerHTML = `
<h3>${a.nome}</h3>
<p>💈 ${a.barbeiro}</p>
<p>📅 ${a.data}</p>
<p>⏰ ${a.horario}</p>
<p>💰 R$ ${a.valor}</p>
<p>📌 ${a.status || "pendente"}</p>
`

const acoes = document.createElement("div")
acoes.className = "acoes-card"

acoes.appendChild(btnAvisar)
acoes.appendChild(btnFinalizar)
acoes.appendChild(btnCancelar)

item.appendChild(acoes)
container.appendChild(item)

})

})
.catch(err => {
console.log("Erro ao carregar agenda:", err)
})

}

// ✅ FINALIZAR
function finalizar(nome, data, horario){
fetch(`${API}/finalizar`,{
method:"POST",
headers:{ "Content-Type":"application/json" },
body: JSON.stringify({ nome, data, horario })
})
.then(() => {
alert("Atendimento finalizado!")
carregarAgenda()
})
.catch(err => console.log(err))
}

// ❌ CANCELAR
function cancelar(nome, data, horario){
if(!confirm("Cancelar agendamento?")) return

fetch(`${API}/cancelar`,{
method:"POST",
headers:{ "Content-Type":"application/json" },
body: JSON.stringify({ nome, data, horario })
})
.then(() => {
alert("Cancelado!")
carregarAgenda()
})
.catch(err => console.log(err))
}

// 🔔 PRÓXIMO
function mostrarProximo(lista){

const agora = new Date()

const futuros = lista.filter(a => {
  const dataHora = new Date(`${a.data}T${a.horario}`)
  return dataHora >= agora && a.status !== "finalizado"
})

if(futuros.length === 0){
  document.getElementById("proximo").innerText = "Sem próximos atendimentos"
  return
}

futuros.sort((a,b)=>{
  return new Date(`${a.data}T${a.horario}`) - new Date(`${b.data}T${b.horario}`)
})

const p = futuros[0]

document.getElementById("proximo").innerText =
`🔔 Próximo: ${p.nome} às ${p.horario}`

}

// 📊 RELATÓRIO
function carregarRelatorio(){

const data = document.getElementById("dataRelatorio").value

if(!data){
  alert("Escolha uma data")
  return
}

fetch(`${API}/relatorio?data=${data}`)
.then(res => res.json())
.then(dados => {

let html = `<h3>Total do dia: R$ ${dados.total_dia || 0}</h3>`

dados.barbeiros.forEach(b => {
  html += `
  <div class="card-relatorio">
    <p><strong>${b.nome}</strong></p>
    <p>Cortes: ${b.quantidade}</p>
    <p>Faturamento: R$ ${b.total}</p>
  </div>
  `
})

document.getElementById("resultadoRelatorio").innerHTML = html

})
.catch(err => {
console.log("Erro relatório:", err)
})

}

// 🚀 INICIAR
window.onload = carregarAgenda