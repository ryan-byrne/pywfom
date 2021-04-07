import { useState, useEffect } from 'react';

// Bootstrap Component
import Tabs from 'react-bootstrap/Tabs';
import Tab from 'react-bootstrap/Tab';
import Modal from 'react-bootstrap/Modal';
import Image from 'react-bootstrap/Image';

// Popup Components
import Start from './popups/Start';
import LoadConfig from './popups/LoadConfig';
import SaveConfig from './popups/SaveConfig';
import LoadSettings from './popups/LoadSettings';

// Each Tab's Components
import File from './tabs/File/Main';
import Cameras from './tabs/Cameras/Main';
import Arduino from './tabs/Arduino/Main';

import arduinoIcon from './img/arduino.png';
import runIcon from './img/run.png';
import camIcon from './img/cam.png';

const Popup = (props) => {
  return (
    <div>{
        <Modal show={props.visible} onHide={props.onHide}>
          {props.content}
        </Modal>
      }</div>
  )
}

export default function Main() {

  const [popup, setPopup] = useState({visible:false,content:null});

  const [config, setConfig] = useState({arduino:{},file:{},cameras:[]})

  const hidePopup = () => setPopup({...popup, visible:false})

  const handleStart = () => setPopup({
    visible:true,
    content:<Start onHide={hidePopup} config={config}/>
  })

  const handleLoad = () => setPopup({
    visible:true,
    content:<LoadConfig onHide={hidePopup}/>
  })

  const handleSave = () => setPopup({
    visible:true,
    content:<SaveConfig onHide={hidePopup} config={config}/>
  })

  const handleLoadDefault = async () => {
    const resp = await fetch('/api/file/default');
    const data = await resp.json();
    setPopup({
      visible:true,
      content:<LoadSettings question="Load Default Settings?" settings={data}
      onYes={(e)=>deploySettings(data)} onNo={hidePopup}/>
    })
  }

  const clearSettings =  async () => {
    const resp = await fetch('/api/system', {method:"DELETE"});
    if (resp.ok) {setConfig({file:{},cameras:[],arduino:{}})}
    return null;
  }

  const deploySettings = (data) => {
    //Clear all current settings
    fetch('/api/system', {method:"DELETE"})
      .then(resp=> {
        if(resp.ok){
          fetch('/api/system', {
            method: "POST",
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)})
            .then(resp => {
              if (resp.ok) { return resp.json()}
              else { console.error(resp.message) }
            })
            .then(data => setConfig(data))
          }
      })
    // Deploy settings to the System
  }

  const handleSaveDefault = () => {}

  useEffect(()=> {
    // get current system settings (even after refresh)
    fetch('/api/system')
      .then(resp => {if(resp.ok){return resp.json()}})
      .then(data => setConfig(data))
  },[]);

  return (
    <div>
      {
        <Tabs defaultActiveKey="profile" id="uncontrolled-tab-example">
          <Tab eventKey='runTab' title={<span><img height="25px" src={runIcon}/> Run</span>}>
            <File config={config} setConfig={setConfig} handleStart={handleStart}
              handleLoad={handleLoad} handleSave={handleSave} handleClose={clearSettings}
              handleLoadDefault={handleLoadDefault} handleSaveDefault={handleSaveDefault}/>
          </Tab>
          <Tab eventKey='camerasTab' title={<span><img height="25px" src={camIcon}/> Cameras</span>}>
            <Cameras config={config} setConfig={setConfig}/>
          </Tab>
          <Tab eventKey='arduinoTab' title={<span><img height="25px" src={arduinoIcon}/> Arduino</span>}>
            <Arduino config={config} setConfig={setConfig}/>
          </Tab>
        </Tabs>
      }
      <Popup content={popup.content} visible={popup.visible} onHide={hidePopup}/>
    </div>
  )
}
