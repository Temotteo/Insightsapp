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
    fetch(`/tarefas_diarias/${data}`, {
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


function carregarAudio(id, modal) {
    $.get(`/carragar_Audio/${id}`, function(data) {
        $('#modbody').empty();

        // Verifica se data é um array
        if (Array.isArray(data)) {
            // Se for um array de objetos
            data.forEach(function(item) {
                var linha = `<p><strong>${item.audio}</strong> <a href="#" onclick="$('#audio_${item.id}').removeClass('d-none').addClass('d-flex'); return false;"><i class="fa fa-audio-description"></i>play</a>
                               <a href="/deletar_audio/${item.id}" class="text-danger" onclick="return confirm('Tem certeza que deseja remover o audio?')"><i class="fa fa-trash-alt" ></i></a>
                               <audio id="audio_${item.id}" class="d-none" controls>
                                  <source src="{{ url_for('static', filename='audios/' + item.audio) }}" type="audio/mpeg">
                                  Your browser does not support the audio element.
                              </audio> 
                             </p>`;
                $('#modbody').append(linha);
            });
        } else {
            // Se data não for um array (caso de apenas um objeto)
            var linha = `<p>escreva audio<strong>${data.audio}</strong> <a href="#" onclick="$('#audio_${data.id}').removeClass('d-none').addClass('d-flex'); return false;">play</a>
                              
                           <audio id="audio_${data.id}" class="d-none" controls>
                              <source src="{{ url_for('static', filename='audios/' + data.audio) }}" type="audio/mpeg">
                              Your browser does not support the audio element.
                          </audio> 
                        </p>`;
            $('#modbody').append(linha);
        }

        // Abre o modal após carregar os dados
        $('#ModalAudio').modal('show');
    });
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
        
