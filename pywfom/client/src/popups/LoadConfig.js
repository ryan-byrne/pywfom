import {useState, useEffect} from 'react';

import Modal from 'react-bootstrap/Modal';
import Button from 'react-bootstrap/Button';
import ButtonGroup from 'react-bootstrap/ButtonGroup';
import Table from 'react-bootstrap/Table';

export default function LoadConfig(props){

  const [configs, setConfigs] = useState({});

  const handleLoad = (config) => {
    props.setArduino(config.arduino);
    props.setCameras(config.cameras);
    props.setFile(config.file);
  }

  useEffect(() => {
    fetch('/api/file')
      .then( resp => { if (resp.ok) {return resp.json()} })
      .then( data => setConfigs(data) )
  },[]);

  return(
    <div>{
        <div>
          <Modal.Header>
            <Modal.Title>Saved Configurations:</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <Table>
            {
              Object.entries(configs).map(([setting, value], idx) => {
                return (
                  <tr>
                    <td>{setting}</td>
                    <td><Button variant="secondary">Delete</Button></td>
                    <td><Button onClick={()=>handleLoad(value)}>Load</Button></td>
                  </tr>
                )
              })
            }
            </Table>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={props.onHide}>Close</Button>
          </Modal.Footer>
        </div>
      }</div>
  )
}
