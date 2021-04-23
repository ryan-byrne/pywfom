import {useEffect, useState} from 'react';

import Modal from 'react-bootstrap/Modal';
import Table from 'react-bootstrap/Table';
import Container from 'react-bootstrap/Container';
import Button from 'react-bootstrap/Button';
import Alert from 'react-bootstrap/Alert';

export default function StartAcquisition(props) {

  const [errors, setErrors] = useState([]);
  const [details, setDetails] = useState(false);

  const handleStart = () => {
    fetch('/api/system/acquisition', {method:['POST']})
      .then(resp=>{
        if (resp.ok) {
          props.setAcquiring(true);
          props.onHide();
        } else {
          resp.text().then(txt=>{
            setErrors([...errors, txt])
          })
        }
      })
  }

  const calculateTotalSize = () => {
    const units = {"sec":1, "min":60, "hr":3600};
    const {number_of_runs, run_length, run_length_unit, framerate, size} = props.config.file;
    const sizeInBytes = number_of_runs*run_length*units[run_length_unit]*framerate*size;
    if (sizeInBytes > 1000000000){
      return `${sizeInBytes/1000000000} GB`
    } else {
      return `${sizeInBytes/1000000} MB`
    }
    console.log(sizeInBytes);
  }

  useEffect(() => {
    setErrors([]);
    fetch('/api/system/acquisition')
      .then(resp=>resp.json().then(data=>setErrors(data)))
  },[])

  return(
    <div>{
        <div>
          <Modal.Header>
            <Modal.Title>Acquisition</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            {
              errors.length > 0 ?
              <Alert variant="danger">
                <Alert.Heading>The Following Error(s) Occured:</Alert.Heading>
                <ul>{errors.map(err=><li key={err}>{err}</li>)}</ul>
              </Alert> :
              <Alert variant="success">
                <Alert.Heading>Ready</Alert.Heading>
              </Alert>

            }
            <Button onClick={()=>setDetails(!details)}>{details?"Hide":"View"} Details</Button>
            <div>
              {
                !details?null:
                <Table>
                  <tbody>
                    <tr><th>User</th><td>{props.config.username}</td></tr>
                    <tr><th>Mouse</th><td>{props.config.mouse}</td></tr>
                    <tr><th>Save Directory</th><td>{props.config.file.directory}</td></tr>
                    <tr><th>Number of Runs</th><td>{props.config.file.number_of_runs}</td></tr>
                    <tr><th>Run Length</th><td>{props.config.file.run_length} {props.config.file.run_length_unit}</td></tr>
                    <tr>
                      <th>Estimated Disk Space Used</th>
                      <td>{calculateTotalSize()}</td>
                    </tr>
                  </tbody>
                </Table>
            }
            </div>
          </Modal.Body>
          <Modal.Footer>
            <Button onClick={props.onHide} variant='secondary'>Cancel</Button>
            <Button onClick={handleStart} disabled={errors.length>0}>Start</Button>
          </Modal.Footer>
        </div>
      }</div>
  )
}
