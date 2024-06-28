function carregarDados() {
      $.get('/saltar_org_id', function(data) {
          $('#modalTableBody').empty();
          data.forEach(function(item) {
              var linha = `<tr>
                              <td>${item.id}</td>
                              <td>${item.nome}</td>
                              <td>${item.Saldo}</td>
                              <td>
                                  <button class="btn btn-primary btn-sm" onclick="verDetalhes('${item.id}')">
                                      <span class="glyphicon glyphicon-eye-open" aria-hidden="true"></span> Ver
                                  </button>
                              </td>
                          </tr>`;
              $('#modalTableBody').append(linha);
          });
          // Abre o modal após carregar os dados
          $('#Modal').modal('show');
      });
  }

  function smsGrupo() {
    
        $('#modalBodySms').empty();
            var linha = `<div class="form-group">
                             <label for="country" class="form-label">Grupo</label>
                              <select class="form-control" id="country"  name ="grupo" >
                                <option value="">selecione...</option>
                            `
                            $.get('/selecionar_group', function(data)
                             {data.forEach(function(item) {`
                                 <option value="${item.id}">${item.nome}</option>
                             </select>
                            </div>
                                <button class="btn btn-primary btn-sm" onclick="enviar_sms_grupo('${item.id}')">
                                    <span class="glyphicon glyphicon-eye-open" aria-hidden="true"></span> Ver
                                </button>
                           `;
            $('#modalBodySms').append(linha);
        });
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

  function enviar_sms_grupo(id) {
    fetch(`/enviar_sms_grupo/${id}`, {
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
