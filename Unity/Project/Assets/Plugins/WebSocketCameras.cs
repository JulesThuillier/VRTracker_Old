using UnityEngine;
using System.Collections;
using WebSocketSharp;

public class WebSocketCameras : MonoBehaviour {

	private WebSocket ws;
	private bool detecting = false;
	private Vector3 position;
	private Vector3 position2;
	private string GatewayIP = "192.168.1.101"; // Set your gateway IP here
	private string WebsocketPort = "9014";
	Camera mainCam;


	void Start () {

		// Retrieve the main camera
		mainCam = Camera.main; 

		// Create and Open the websocket
		ws = new WebSocket("ws://"+ GatewayIP + ":" + WebsocketPort);
		ws.OnOpen += OnOpenHandler;
		ws.OnMessage += OnMessageHandler;
		ws.OnClose += OnCloseHandler;

		ws.ConnectAsync();

	}

	private void OnOpenHandler(object sender, System.EventArgs e) {
		Debug.Log("WebSocket connected!");
	}

	private void OnMessageHandler(object sender, MessageEventArgs e) {
 		
		// Split the position in XYZ
		string[] temp = e.Data.Split("|"[0]);

		position[0] = float.Parse(temp[0]);
		position[1] = float.Parse(temp[2]);
		position[2] = float.Parse(temp[1]);

		// Here you can add some post treatment on the position (remove weird datas, add a Kalman filter, smoothen the curve...


	/*	if (Mathf.Abs (position2 [0] - position [0]) > 20 || Mathf.Abs (position2 [1] - position [1]) > 20 || Mathf.Abs (position2 [2] - position [2]) > 20) {
			Debug.Log ("Error");
		} else {
			position = position2;
			Debug.Log (position);

		}
*/

	}
	private void OnCloseHandler(object sender, CloseEventArgs e) {
		Debug.Log("WebSocket closed with reason: " + e.Reason);
	}
	private void OnSendComplete(bool success) {
		Debug.Log("Message sent successfully? " + success);
	}

	// Update is called once per frame
	void Update () {

		// Press space to start tracking
		if (Input.GetKeyDown ("space")) {
			print ("Starting to track !");
			ws.SendAsync ("start", OnSendComplete);
		} 

		// Press d to detect the cameras (this is for calibration purposes)
		else if (Input.GetKeyDown ("d")) {
			if (detecting) {
				print ("Stop searching for cameras..");
				ws.SendAsync ("end detection", OnSendComplete);
			} else {
				print ("Searching for cameras..");
				ws.SendAsync ("detect", OnSendComplete);
			
			}
			detecting = !detecting;
		} 


		else if (Input.GetKeyDown ("c")) {
			position = position2;
		}

		mainCam.transform.position = position;
	}
	
}
