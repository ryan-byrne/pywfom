import { useState, useEffect } from 'react';

// Bootstrap Component
import Tabs from 'react-bootstrap/Tabs';
import Tab from 'react-bootstrap/Tab';
import Modal from 'react-bootstrap/Modal';
import Image from 'react-bootstrap/Image';
import Container from 'react-bootstrap/Container';

// Popup Components
import LoadConfig from './popups/LoadConfig';
import SaveConfig from './popups/SaveConfig';
import YesNo from './popups/YesNo';
import MakeDefault from './popups/MakeDefault';
import StartAcquisition from './popups/StartAcquisition';

// Each Tab's Components
import File from './tabs/File/Main';
import Cameras from './tabs/Cameras/Main';
import Arduino from './tabs/Arduino/Main';
import Viewer from './tabs/Viewer/Main';

// Windows
import Acquisition from './windows/Acquisition';
import Error from './windows/Error';
import Login from './windows/Login';
import Register from './windows/Register';

// Images
import arduinoIcon from './img/arduino.png';
import runIcon from './img/run.png';
import camIcon from './img/cam.png';
import viewIcon from './img/view.png';

const Popup = (props) => {

  return (
    <div>{
        <Modal show={props.visible} onHide={props.onHide}>
          {props.content}
          {props.status}
        </Modal>
      }</div>
  )
}

export default function Main() {

  const [popup, setPopup] = useState({visible:false,content:null});
  const [acquiring, setAcquiring] = useState(false);
  const [error, setError] = useState(false);
  const [loggedIn, setLoggedIn] = useState(false);
  const [viewing, setViewing] = useState(false);
  const [registering, setRegistering] = useState(false)
  const [config, setConfig] = useState({arduino:{},file:{},cameras:[],username:"",mouse:"",name:""})

  const hidePopup = () => setPopup({...popup, visible:false})

  const handleStart = () => setPopup({
    visible:true,
    content:<StartAcquisition onHide={hidePopup} config={config} setAcquiring={setAcquiring}/>
  })

  const handleLoad = () => setPopup({
    visible:true,
    content:<LoadConfig user={config.username} name={config.name} onHide={hidePopup} deploy={deploySettings}/>
  });

  const handleSave = () => setPopup({
    visible:true,
    content:<SaveConfig onHide={hidePopup} config={config}/>
  })

  const handleLoadDefault = async () => {
    const user = "ryan";
    const resp = await fetch(`/api/db/default/${user}`);
    const data = await resp.json();
    setPopup({
      visible:true,
      content:<YesNo onYes={()=>deploySettings(data)} onNo={hidePopup} question="Load Default Settings?"/>
    })
  }

  const clearSettings =  async () => {
    fetch('/api/system/settings', {method:"DELETE"}).then(resp=>{
      if (resp.ok) {setConfig({file:{},cameras:[],arduino:{}, username:null});hidePopup();}
    })
  }

  const handleClear = () => setPopup({
    visible:true,
    content:<YesNo question="Close Current Session?" onYes={clearSettings} onNo={hidePopup}/>
  })

  const deploySettings = (data) => {
    //Clear all current settings
    fetch('/api/system/settings', {method:"DELETE"})
      .then(resp=> {
        if(resp.ok){
          fetch('/api/system/settings', {
            method: "POST",
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)})
            .then(resp => {
              if (resp.ok) { resp.json().then( data => setConfig({...data, username:config.username}))}
              else { resp.text().then(txt=>console.error(txt)) }
              setPopup({visible:false})
            })
          }
      })
    // Deploy settings to the System
  }

  const handleSaveDefault = () => setPopup({
    visible:true,
    content:<MakeDefault onHide={hidePopup} config={config}/>
  })

  useEffect(()=>{
    fetch('/api/system/settings/mouse', {
      method: "PUT",
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(config.mouse)}).then(resp=>resp.text().then(txt=>{
        //console.log(txt);
      }))
  },[config.mouse])

  useEffect(()=> {
    // get current system settings (even after refresh)
    fetch('/api/system/settings')
      .then(resp => {
        if(resp.ok){ return resp.json() }
        else { setError(true); }
      })
      .then(data => setConfig(data))
  },[]);

  useEffect(()=>{
    // Calculate the size of the file each time cameras change
    let size = 0;
    let framerate = 0;
    config.cameras.map(cam=>{
      const {height, width, binning} = cam.aoi;
      const pixelSize = parseInt(cam.dtype.substring(4))/8;
      const bin = parseInt(binning.charAt(0));
      framerate = cam.primary ? cam.framerate : framerate;
      size += pixelSize*height*width/bin
    })
    setConfig({...config, file:{...config.file, size:size, framerate:framerate}})
  },[config.cameras])

  return (
    <div>
      {
        error ? <Error/> :
        registering ? <Register onHide={()=>setRegistering(false)} setConfig={setConfig}/> :
        !config.username ? <Login setConfig={setConfig} setRegistering={setRegistering}/> :
        viewing ? <Viewer/> :
        acquiring ? <Acquisition config={config} setAcquiring={setAcquiring}/> :
        <Container>
          <Tabs defaultActiveKey="runTab" id="uncontrolled-tab-example">
            <Tab eventKey='runTab' title={<span><img height="25px" src={runIcon}/> Run</span>}>
              <File config={config} setConfig={setConfig} start={handleStart}
                load={handleLoad} save={()=>handleSave(false)} close={handleClear}
                loadDefault={handleLoadDefault} saveDefault={handleSaveDefault}
                acquiring={acquiring}/>
            </Tab>
            <Tab eventKey='camerasTab' title={<span><img height="25px" src={camIcon}/> Cameras</span>}>
              <Cameras config={config} setConfig={setConfig} acquiring={acquiring}/>
            </Tab>
            <Tab eventKey='arduinoTab' title={<span><img height="25px" src={arduinoIcon}/> Arduino</span>}>
              <Arduino config={config} setConfig={setConfig} acquiring={acquiring}/>
            </Tab>
            <Tab eventKey='viewerTab' title={<span><img height="25px" src={viewIcon}/> Viewer</span>}>
              <Viewer user={config.username}/>
            </Tab>
          </Tabs>
        </Container>
      }
      <Popup content={popup.content} visible={popup.visible} status={popup.status} onHide={hidePopup}/>
    </div>
  )
}
