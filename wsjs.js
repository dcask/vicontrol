let f_inj='<script>function PopUpShow(){$("#popup1").show();} function PopUpHide(){$("#popup1").hide();}</script>';
let inj='<div class="b-popup" id="popup1"><div class="b-popup-content"><span id="popupcontent"></span></br><a href="javascript:PopUpHide()">Close</a></div></div>';
$( document ).ready(function() {
$("body").append(f_inj);
$("body").append(inj);
});
$(document).ready(function(){ PopUpHide();});
let getUrl = window.location;
let baseUrl = getUrl .protocol + "//" + getUrl.host + "/" + getUrl.pathname.split('/')[1];
let client_id = Date.now()
const visSocket = new WebSocket('wss://'+baseUrl+'/control/ws/${client_id}');
visSocket.onmessage = (event) => {
    let c=JSON.parse(event.data);
    console.log(event.data);
    if(c.command=='message')
    {
        if(c.text.startsWith('!')){
            $("#popupcontent").text(c.text.replace('!',''));
            PopUpShow();
        }
    }
}
//let token=JSON.parse(sessionStorage['oidc.user:/idsrv:DashboardsApp'])["access_token"]
//const urlParams = new URLSearchParams(window.location.search);
//const dashboard = urlParams.get('DashboardGuid')
//let command={"command":"auth","token":token,"dashboard":dashboard};
