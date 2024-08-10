function carregarDados() {
      $.get('/saltar_org_id', function(data) {
          $('#modalTableBody').empty();
          data.forEach(function(item) {
              var linha = `<tr>
                              <td>${item.Org_id}</td>
                              <td>${item.Nome}</td>
                              <td>${item.Saldo}</td>
                              <td>
                                  <button class="btn btn-primary btn-sm" onclick="verDetalhes('${item.Org_id}')">
                                      <span class="glyphicon glyphicon-eye-open" aria-hidden="true"></span> Ver
                                  </button>
                              </td>
                          </tr>`;
              $('#modalTableBody').append(linha);
          });
          // Abre o modal após carregar os dados
          $('#ModalOrg').modal('show');
      });
  }

  function smsGrupo() {
   
        $('#modalBodySms').empty();
            var linha = `
                    <div class="form-group">
                        <label for="Sender_id">Sender_id:</label>
                         <input type="text" class="form-control" id="Sender_id" name="Sender_id"  required ></input>
                         </div>
                      <div class="form-group">
                        <label for="mensagem">Mensage:</label>
                         <textarea type="text" class="form-control" id="mensagem" row="5" name="mensagem"  required ></textarea>
                         </div><div class="form-group">
                             <label for="country" class="form-label">Grupo</label>
                              <select class="form-control" id="country"  name ="grupo" >
                                <option value="">selecione...</option>
                            `;
                            $.get('/selecionar_group', function(data) {
                                data.forEach(function(item) {
                                    linha += `<option value="${item.id}">${item.nome}</option>`;
                                });
                        
                                // Fecha a tag select e adiciona o botão de enviar
                                linha += `</select>
                                          </div>
                                          <button class="btn btn-primary btn-sm" onclick="enviar_sms_grupo()">
                                          <span class="glyphicon glyphicon-eye-open" aria-hidden="true"></span> enviar
                                      </button>`;
                                         
            $('#modalBodySms').append(linha);
        
        // Abre o modal após carregar os dados
        $('#ModalSmsGroup').modal('show');
    });
}

function callOne(id) {
   let idd = String(id)
    $('#modalBodySms').empty();
        var linha = `
        <form action ="/start_ivr_campaign" method="post">
        <textarea  name="campaign" rows="1" cols="40" placeholder="Enter Campaign"></textarea>

               <div class="form-group">
                           <textarea name="phone_numbers" rows="1" cols="50" placeholder="Enter phone numbers: +258"></textarea>
                             </div> <div class="form-group">
                         <label for="data" class="form-label">Data:</label>
                             <input type="date" name="data" id="data" class="form-control-sm">
                            </div>
                                      <button class="btn btn-primary btn-sm" type='submit'>
                                          <span class="glyphicon glyphicon-eye-open" aria-hidden="true"></span> enviar
                                      </button>
                                      </form>
                        `;
                    
                                     
        $('#modalBodySms').append(linha);
    
    // Abre o modal após carregar os dados
   
};


function callGrupo(id) {
   
    $('#modalBodySms').empty();
        var linha = `
         <form action ="/start_ivr_teste" method="post">
         <input type="hidden" name="campaign" id="campaign" value="${id}">

                <div class="form-group">
                   </div><div class="form-group">
                         <label for="country" class="form-label">Grupo</label>
                          <select class="form-control" id="call"  name ="numero" >
                            <option value="">selecione...</option>
                            
                        `;
                        $.get('/selecionar_group', function(data) {
                            data.forEach(function(item) {
                                linha += `<option value="${item.id}">${item.nome}</option>`;
                            });
                    
                            // Fecha a tag select e adiciona o botão de enviar
                            linha += `</select>
                                          </div> <div class="form-group">
                         <label for="data" class="form-label">Data:</label>
                             <input type="date" name="data" id="data" class="form-control-sm">
                            </div>
                                      <button class="btn btn-primary btn-sm" type='submit'>
                                          <span class="glyphicon glyphicon-eye-open" aria-hidden="true"></span> enviar
                                      </button>
                                      </form>
                        `;
        $('#modalBodySms').append(linha);
    
    // Abre o modal após carregar os dados
   
});
}


  function verDetalhes(id) {
      fetch(`/get_org/${id}`, {
              method: 'GET'
          })
          .then(response => {
              if (response.redirected) {
                  window.location.href = response.url;
              }
          })
          .catch(error => {
              console.error('Erro ao enviar dados:', error);
          });
  }


  function carragar_grafico() {
    var data = document.getElementById("Data").value;
    fetch(`/tarefas_diarias_data/${data}`, {
            method: 'GET'
        })
        .then(response => {
            if (response.redirected) {
                window.location.href = response.url;
            }
        })
        .catch(error => {
            console.error('Erro ao enviar dados:', error);
        });
}


  function enviar_sms_grupo() {
    var grupoId = $('#country').val();
    var smsData = {
        grupo: grupoId,
        // Adicione outros campos do formulário aqui, se necessário
        mensagem: $('#mensagem').val(), // Supondo que você tenha um campo de mensagem no formulário
           // Supondo que você tenha um campo de contato no formulário
    };

    fetch('/enviar_sms_grupo', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(smsData)
        })
        .then(response => {
            if (response.redirected) {
                window.location.href = response.url;
            } else {
                return response.json();
            }
        })
        .then(data => {
            console.log('Resposta do servidor:', data);
        })
        .catch(error => {
            console.error('Erro ao enviar dados:', error);
        });
}

function selected_Idioma() {
    const selectElement = document.getElementById('idioma');
    const selectedIdioma = selectElement.value;
    fetch(`/idioma_inscricao/${selectedIdioma}`, {
            method: 'GET',
            
        })
        .then(response => {
            if (response.redirected) {
                window.location.href = response.url;
            } else {
                return response.json();
            }
        })
        .then(data => {
            console.log('Resposta do servidor:', data);
        })
        .catch(error => {
            console.error('Erro ao enviar dados:', error);
        });
}


function carregarAudio(value) {
        $('#modbody').empty();
                var linha = ` <audio  controls>
                                  <source src="/static/audios/${value}" type="audio/mpeg">
                                  Your browser does not support the audio element.
                              </audio> 
                             </p>`;
                $('#modbody').append(linha);

        // Abre o modal após carregar os dados
        $('#ModalAudio').modal('show');
   
}

function carragar_questoes() {
    var id = document.getElementById("project").value;
    $('#questoes').text('Buscando as questoes....')
    $.get(`/carragar_questoes/${id}`, function(data) {
        $('#audios').empty();

        // Verifica se data é um array
        if (Array.isArray(data)) {
             var linha = `<label for="questao" class="form-label">Questao</label>
                 <select class="form-control" id="questao"  name ="questao" >
                  <option value="">selecione...</option>`
                  data.forEach(function(item) {
                   linha += `<option value="${item.id}">${item.id}</option>`
                    });
                  linha += `</select>`
                  $('#audios').append(linha);
        }
        $('#questoes').hide();
    });
}

function getAllOptions() {
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0'); // Os meses são baseados em zero
    const day = String(today.getDate()).padStart(2, '0');
    
    const formattedDate = `${year}-${month}-${day}`;
    let select = document.getElementById('action');
    let options = Array.from(select.options).map(option => option.value);

    fetch(`/tarefas_diarias/${formattedDate}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ allOptions: options })
    })
    .then(response => response.json())
    .then(data => {
        console.log('All options:', data);
        alert('All options: ' + data);
    });
}

        
