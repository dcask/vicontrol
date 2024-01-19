//let f_inj='<script>function PopUpShow(){$("#popup1").show();} function PopUpHide(){$("#popup1").hide();}</script>';
//let inj='<div class="b-popup" id="popup1"><div class="b-popup-content"><span id="popupcontent"></span></br><a href="javascript:PopUpHide()">Close</a></div></div>';
let f_inj='<script>function PopUpShow(){$("#admmessage-popup1").css({"visibility":"visible","opacity":1});}function PopUpHide(){$("#admmessage-popup1").css({"visibility":"hidden","opacity":0});}</script>';
let inj=`<div id="admmessage-popup1" class="admmessage-overlay">
<div class="admmessage-popup">
<h2 class="admmessage-h2">Сообщение от администратора</h2>
<a class="admmessage-close" href="javascript:PopUpHide()">&times;</a>
<div id="admmessage-content">
</div>
</div>
</div>
`
let token=JSON.parse(sessionStorage['oidc.user:/idsrv:DashboardsApp'])["access_token"]
const urlParams = new URLSearchParams(window.location.search);
const dashboardguid = urlParams.get('dashboardGuid')
let command={"command":"auth","token":token,"dashboard":dashboardguid};
$( document ).ready(function() {
$("body").append(f_inj);
$("body").append(inj);
});
//$(document).ready(function(){ PopUpHide();});
let getUrl = window.location;
let baseUrl = getUrl.host; //"/" + getUrl.pathname.split('/')[1];
let client_id = Date.now()
const visSocket = new WebSocket('wss://'+baseUrl+"/control/ws/"+client_id);
visSocket.onopen = () => visSocket.send(JSON.stringify(command));
console.log('wss connected');
visSocket.onmessage = (event) => {
    console.log(event.data);
    let c=JSON.parse(event.data);
    
    if(c.command=='message')
    {
       $("#admmessage-content").text(c.text);
       PopUpShow();
    }
}

