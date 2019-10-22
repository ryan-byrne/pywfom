package jsplassh.views;

import com.fazecast.jSerialComm.SerialPort;
import java.awt.Color;
import java.awt.EventQueue;
import java.awt.Font;
import java.awt.Toolkit;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import javax.swing.AbstractListModel;
import javax.swing.ImageIcon;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JList;
import javax.swing.JPanel;
import javax.swing.JSeparator;
import javax.swing.JSlider;
import javax.swing.JTextField;
import javax.swing.SwingConstants;
import javax.swing.UIManager;
import javax.swing.border.EmptyBorder;
import javax.swing.event.ChangeEvent;
import javax.swing.event.ChangeListener;

import org.json.JSONObject;
import org.json.JSONTokener;
import java.awt.event.InputMethodListener;
import java.awt.event.InputMethodEvent;
import javax.swing.JCheckBox;
import java.beans.PropertyChangeListener;
import java.beans.PropertyChangeEvent;

public class jsplassh_window extends JFrame {
	
	
	private JPanel contentPane;
	List<String> orderList = new ArrayList<String>();
	String orderString = new String();
	int arduinoState = 0;
	int ledState = 0;
	int solisState = 0;
	int mode = 1;
	boolean st; 
	boolean ledOn[] = {false, false, false, false};
	String colors[] = {"Blue","Green","Lime","Red"};
	String mouse = new String();
	String uni = new String();
	boolean readyToDeploy = false;
	private JTextField framerate;
	private JTextField setHeight;
	private JTextField exposureTime;
	private JTextField setWidth;
	private JTextField setBottom;
	private JTextField setTop;
	private JTextField runningTime;
	private JTextField numStim;
	private JTextField numRuns;

	/**
	 * Launch the application.
	 */
	public static void main(String[] args) {
		try {
			UIManager.setLookAndFeel("com.sun.java.swing.plaf.windows.WindowsLookAndFeel");
		} catch (Throwable e) {
			e.printStackTrace();
		}
		EventQueue.invokeLater(new Runnable() {
			public void run() {
				try {
					jsplassh_window frame = new jsplassh_window();
					frame.setVisible(true);
				} catch (Exception e) {
					e.printStackTrace();
				}
			}
		});
	}

	/**
	 * Create the frame.
	 */
	public jsplassh_window() {
		setResizable(false);
		initComponents();
	}
	private void initComponents() {
		OutputStream out = initializeArduino();
		setTitle("WFOM Dashboard");
		setIconImage(Toolkit.getDefaultToolkit().getImage(jsplassh_window.class.getResource("/jsplassh/resources/download.jpg")));
		setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		setBounds(100, 100, 330, 600);
		contentPane = new JPanel();
		contentPane.setBorder(new EmptyBorder(5, 5, 5, 5));
		setContentPane(contentPane);
		
		JLabel lblSolisParameters = new JLabel("Zyla Parameters");
		lblSolisParameters.setFont(new Font("Tahoma", Font.BOLD | Font.ITALIC, 11));
		lblSolisParameters.setBounds(5, 5, 120, 14);
		
		JSlider binning = new JSlider();
		binning.setSnapToTicks(true);
		binning.setPaintTicks(true);
		binning.setBounds(15, 45, 43, 111);
		binning.setToolTipText("");
		binning.setOrientation(SwingConstants.VERTICAL);
		binning.setMajorTickSpacing(1);
		binning.setMaximum(4);
		binning.setMinimum(1);
		
		JLabel lblBinning = new JLabel("Binning");
		lblBinning.setBounds(42, 30, 34, 14);
		
		JLabel lblSetFramerate = new JLabel("Set Framerate (fps)");
		lblSetFramerate.setBounds(110, 30, 95, 14);
		lblSetFramerate.setEnabled(false);
		
		framerate = new JTextField();
		framerate.setHorizontalAlignment(SwingConstants.CENTER);
		framerate.setBounds(110, 45, 86, 20);
		framerate.setEnabled(false);
		framerate.setText("50.70");
		framerate.setColumns(10);
		
		JLabel lblSetHeight = new JLabel("Set Height");
		lblSetHeight.setBounds(214, 30, 50, 14);
		
		setHeight = new JTextField();
		setHeight.setHorizontalAlignment(SwingConstants.CENTER);
		setHeight.setBounds(214, 45, 86, 20);
		setHeight.setText("2048");
		setHeight.setColumns(10);
		
		JLabel lblExposureTimes = new JLabel("Exposure Time (s)");
		lblExposureTimes.setBounds(110, 71, 86, 14);
		
		exposureTime = new JTextField();
		exposureTime.setHorizontalAlignment(SwingConstants.CENTER);
		exposureTime.setBounds(110, 91, 86, 20);
		exposureTime.setText("0.0068");
		exposureTime.setColumns(10);
		
		JLabel lblSetWidth = new JLabel("Set Width");
		lblSetWidth.setBounds(214, 71, 47, 14);
		
		setWidth = new JTextField();
		setWidth.setHorizontalAlignment(SwingConstants.CENTER);
		setWidth.setBounds(214, 91, 86, 20);
		setWidth.setText("2048");
		setWidth.setColumns(10);
		
		JLabel lblx = new JLabel("1x1");
		lblx.setBounds(68, 45, 18, 14);
		
		JLabel lblx_1 = new JLabel("2x2");
		lblx_1.setBounds(68, 77, 18, 14);
		
		JLabel lblx_2 = new JLabel("4x4");
		lblx_2.setBounds(68, 110, 18, 14);
		
		JLabel lblx_3 = new JLabel("8x8");
		lblx_3.setBounds(68, 142, 18, 14);
		
		JLabel lblLedControl = new JLabel("LED Control");
		lblLedControl.setFont(new Font("Tahoma", Font.BOLD | Font.ITALIC, 11));
		lblLedControl.setBounds(15, 190, 84, 14);
		
		JLabel lblOrder_1 = new JLabel("Strobe Order");
		lblOrder_1.setBounds(135, 240, 63, 14);
		
		JLabel lblLeds = new JLabel("LEDs");
		lblLeds.setBounds(46, 215, 23, 14);
		
		JButton btnDeploySettingsTo_1 = new JButton("Deploy Settings to Camera");
		btnDeploySettingsTo_1.setBounds(68, 537, 175, 23);
		btnDeploySettingsTo_1.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				int binVal = (int) (16*Math.exp(-0.693*binning.getValue()));
				String b = binVal+"x"+binVal;
				String h = setHeight.getText();
				String w = setWidth.getText();
				String e = exposureTime.getText();
				List<String> s = orderList;
				String f = framerate.getText();
				String u = uni;
				String m = mouse;
				String btm = setBottom.getText();
				String top = setTop.getText();
				String r = numRuns.getText();
				String len = runningTime.getText();
				try {
					writeJsonSettings(b, f, h, e, w, s, u, m,  btm, top, r, len, st);
					System.exit(0);
				} catch (Exception e1) {
					// TODO Auto-generated catch block
					System.out.println(e1.getMessage());
				}
			}

		});
		JList list = new JList();
		JLabel lblStrobeOrder = new JLabel();
		lblStrobeOrder.setBounds(264, 235, 0, 0);
		
		JButton btnRed = new JButton("Red");
		btnRed.setBounds(15, 235, 84, 23);
		btnRed.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				if (mode == 0) {
					controlLeds(arg0, out);
				}
				else {
					updateStrobeOrder(arg0, list, out);
					btnRed.setEnabled(false);
					lblStrobeOrder.setText(orderString);	
				}
			}
		});
		btnRed.setForeground(Color.RED);
		
		JButton btnGreen = new JButton("Green");
		btnGreen.setBounds(15, 264, 84, 23);
		btnGreen.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				if (mode == 0) {
					controlLeds(arg0, out);
				}
				else {
					updateStrobeOrder(arg0, list, out);
					btnGreen.setEnabled(false);
					lblStrobeOrder.setText(orderString);	
				}
			}
		});
		btnGreen.setForeground(Color.GREEN);
		
		JButton btnBlue = new JButton("Blue");
		btnBlue.setBounds(15, 293, 84, 23);
		btnBlue.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				if (mode == 0) {
					controlLeds(arg0, out);
				}
				else {
					updateStrobeOrder(arg0, list, out);
					btnBlue.setEnabled(false);
					lblStrobeOrder.setText(orderString);	
				}
			}
		});
		btnBlue.setForeground(Color.BLUE);
		
		JButton btnSpeckle = new JButton("Lime");
		btnSpeckle.setBounds(15, 324, 84, 23);
		btnSpeckle.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				if (mode == 0) {
					controlLeds(arg0, out);
				}
				else {
					updateStrobeOrder(arg0, list, out);
					btnSpeckle.setEnabled(false);
					lblStrobeOrder.setText(orderString);	
				}
			}
		});
		btnSpeckle.setForeground(new Color(0, 255, 0));
		contentPane.setLayout(null);
		contentPane.add(btnRed);
		contentPane.add(btnGreen);
		contentPane.add(btnBlue);
		contentPane.add(btnSpeckle);
		contentPane.add(btnDeploySettingsTo_1);
		contentPane.add(lblSolisParameters);
		contentPane.add(lblLedControl);
		contentPane.add(lblStrobeOrder);
		contentPane.add(lblLeds);
		contentPane.add(lblOrder_1);
		contentPane.add(binning);
		contentPane.add(lblx_2);
		contentPane.add(lblx_1);
		contentPane.add(lblx_3);
		contentPane.add(lblx);
		contentPane.add(lblBinning);
		contentPane.add(exposureTime);
		contentPane.add(lblExposureTimes);
		contentPane.add(framerate);
		contentPane.add(lblSetFramerate);
		contentPane.add(setHeight);
		contentPane.add(setWidth);
		contentPane.add(lblSetWidth);
		contentPane.add(lblSetHeight);
		
		JSeparator separator = new JSeparator();
		separator.setBounds(5, 172, 295, 7);
		contentPane.add(separator);
		
		JSeparator separator_1 = new JSeparator();
		separator_1.setBounds(10, 361, 290, 5);
		contentPane.add(separator_1);;
		
		JLabel lblMode = new JLabel("Mode");
		lblMode.setHorizontalAlignment(SwingConstants.CENTER);
		lblMode.setBounds(198, 190, 46, 14);
		contentPane.add(lblMode);
		
		JLabel lblTestLights = new JLabel("Test LEDs");
		lblTestLights.setBounds(155, 215, 47, 14);
		contentPane.add(lblTestLights);
		
		JLabel lblSetOrder = new JLabel("Set Order");
		lblSetOrder.setBounds(242, 215, 58, 14);
		contentPane.add(lblSetOrder);
		list.setVisibleRowCount(4);
		list.setBounds(121, 260, 84, 72);
		contentPane.add(list);
		
		JButton btnClear = new JButton("Clear");
		btnClear.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				updateStrobeOrder(arg0,list, out);
				btnBlue.setEnabled(true);
				btnGreen.setEnabled(true);
				btnRed.setEnabled(true);
				btnSpeckle.setEnabled(true);
			}
		});
		btnClear.setBounds(214, 279, 66, 23);
		contentPane.add(btnClear);
		
		JSlider slider = new JSlider();
		slider.addChangeListener(new ChangeListener() {
			int c = 0;
			public void stateChanged(ChangeEvent e) {
				c++;
				if (c >= 3) {
					mode = slider.getValue();
					c = 0;
					String message = "";
					if (mode == 1) {
						message = "Set Order";
					}
					else {
						message = "LED Test";
						orderList.clear();
						String[] orderArray = new String[orderList.size()];
						orderList.toArray(orderArray);
						list.setModel(new AbstractListModel() {
							public int getSize() {
								return orderArray.length;
							}
							public Object getElementAt(int index) {
								return((index+1)+". "+orderArray[index]);
							}
						});
					}
					System.out.println("Mode set to: "+message);
				}
				if (mode == 0) {
					list.setEnabled(false);
					btnClear.setEnabled(false);
					btnBlue.setEnabled(true);
					btnGreen.setEnabled(true);
					btnRed.setEnabled(true);
					btnSpeckle.setEnabled(true);
				}
				else {
					list.setEnabled(true);
					btnClear.setEnabled(true);
				}

			}
		});
		slider.setMaximum(1);
		slider.setBounds(204, 215, 34, 14);
		contentPane.add(slider);
		
		JLabel lblBottom = new JLabel("Bottom");
		lblBottom.setBounds(110, 116, 86, 14);
		contentPane.add(lblBottom);
		
		setBottom = new JTextField();
		setBottom.setHorizontalAlignment(SwingConstants.CENTER);
		setBottom.setText("1");
		setBottom.setColumns(10);
		setBottom.setBounds(110, 136, 86, 20);
		contentPane.add(setBottom);
		
		JLabel lblTop = new JLabel("Top");
		lblTop.setBounds(214, 116, 86, 14);
		contentPane.add(lblTop);
		
		setTop = new JTextField();
		setTop.setHorizontalAlignment(SwingConstants.CENTER);
		setTop.setText("1");
		setTop.setColumns(10);
		setTop.setBounds(214, 136, 86, 20);
		contentPane.add(setTop);
		
		JCheckBox chckbxStim = new JCheckBox("Stim Functionality");
		chckbxStim.addPropertyChangeListener(new PropertyChangeListener() {
			public void propertyChange(PropertyChangeEvent e) {
				if (e.getNewValue().toString() == "CHECKEDHOT") {
					runningTime.setEnabled(true);
					numStim.setEnabled(true);
					numRuns.setEnabled(true);
				}
				else if (e.getNewValue().toString() == "UNCHECKEDHOT") {
					runningTime.setEnabled(false);
					numStim.setEnabled(false);
					numRuns.setEnabled(false);
				}
				else {
					return;
				}
			}
		});
		chckbxStim.setBounds(108, 373, 109, 23);
		contentPane.add(chckbxStim);
		
		runningTime = new JTextField();
		runningTime.setHorizontalAlignment(SwingConstants.CENTER);
		runningTime.setEnabled(false);
		runningTime.setText("5.000");
		runningTime.setColumns(10);
		runningTime.setBounds(46, 403, 86, 20);
		contentPane.add(runningTime);
		
		numStim = new JTextField();
		numStim.setHorizontalAlignment(SwingConstants.CENTER);
		numStim.setEnabled(false);
		numStim.setText("1");
		numStim.setColumns(10);
		numStim.setBounds(178, 403, 86, 20);
		contentPane.add(numStim);
		
		JLabel lblStimLengths = new JLabel("Stim Length (s)");
		lblStimLengths.setBounds(46, 427, 86, 14);
		contentPane.add(lblStimLengths);
		
		JLabel lblNumberOfStims = new JLabel("Number of Stims");
		lblNumberOfStims.setBounds(178, 427, 86, 14);
		contentPane.add(lblNumberOfStims);
		
		numRuns = new JTextField();
		numRuns.setHorizontalAlignment(SwingConstants.CENTER);
		numRuns.setText("1");
		numRuns.setEnabled(false);
		numRuns.setColumns(10);
		numRuns.setBounds(110, 452, 86, 20);
		contentPane.add(numRuns);
		
		JLabel numRunslbl = new JLabel("# of Runs");
		numRunslbl.setHorizontalAlignment(SwingConstants.CENTER);
		numRunslbl.setBounds(110, 475, 86, 14);
		contentPane.add(numRunslbl);
	}
	
	public OutputStream initializeArduino() {
		SerialPort sp = SerialPort.getCommPort("COM4");
		sp.setComPortParameters(115200, 8, 1, 0);
		sp.setComPortTimeouts(SerialPort.TIMEOUT_WRITE_BLOCKING, 0, 0);
		if (sp.openPort()) {
			System.out.println("Arduino is connected.");
		}
		else {
			System.out.println("Arduino is not connected");
		}
		return sp.getOutputStream();
	}

	private void updateStrobeOrder(java.awt.event.ActionEvent e, JList l, OutputStream out) {
		
		if(e.getActionCommand().toString() == "Clear"){
			orderList.clear();
		}
		else if ((mode == 0)) {
			controlLeds(e, out);
		}
		else {
			orderList.add(e.getActionCommand().toString());
		}
		String[] orderArray = new String[orderList.size()];
		orderList.toArray(orderArray);
		l.setModel(new AbstractListModel() {
			public int getSize() {
				return orderArray.length;
			}
			public Object getElementAt(int index) {
				return((index+1)+". "+orderArray[index]);
			}
		});

	}
	
	private void controlLeds(ActionEvent e, OutputStream out) {
		String button = e.getActionCommand().toString();
		int i = Arrays.asList(colors).indexOf(button);
		ledOn[i] = !ledOn[i];
		String message = new String();
		for(boolean b:ledOn) {
			if (!b) {
				message += "0";
			}
			else {
				message += "1";
			}
		}
		try {
			System.out.println("Sending "+ message +" to arduino");
			out.write(message.getBytes());
			out.flush();
		} catch (IOException e1) {
			// TODO Auto-generated catch block
			e1.printStackTrace();
		}
	}
	
	private void writeJsonSettings(String b, String f, String h, String e, String w, List<String> s, String u, String m, String btm, String top, String r, String len, Boolean st) throws Exception {
		FileReader reader;
		if (s.size() < 1) {
			throw new Exception("The length of the Strobe Array must be greater than 0!");
		}
		reader = new FileReader("settings.json");
		JSONTokener tokener = new JSONTokener(reader);
		JSONObject settings = new JSONObject(tokener);
		reader.close();
		JSONObject camera = new JSONObject();
		camera.put("binning", b);
		camera.put("height", h);
		camera.put("bottom", btm);
		camera.put("width", w);
		camera.put("top", top);
		camera.put("exposure_time", e);
		camera.put("framerate", f);
		if (st == true) {
			JSONObject stim = new JSONObject();
			stim.put("run_duration", r);
			stim.put("stim_length", len);
			settings.put("stim", stim);
		}
		else {
			settings.put("stim", "Not enabled");
		}
		settings.put("strobe_order", s);
		settings.put("camera", camera);
		PrintWriter out = new PrintWriter("settings.json");
		out.println(settings.toString());
		out.close();
	}
}
