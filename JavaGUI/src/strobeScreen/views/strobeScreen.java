package strobeScreen.views;

import com.fazecast.jSerialComm.SerialPort;
import java.awt.Color;
import java.awt.EventQueue;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.FileReader;
import java.io.IOException;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import javax.swing.AbstractListModel;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JList;
import javax.swing.JPanel;
import javax.swing.JSlider;
import javax.swing.SwingConstants;
import javax.swing.UIManager;
import javax.swing.border.EmptyBorder;
import javax.swing.event.ChangeEvent;
import javax.swing.event.ChangeListener;

import org.json.JSONObject;
import org.json.JSONTokener;

public class strobeScreen extends JFrame {
	
	
	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;
	private JPanel contentPane;
	List<String> orderList = new ArrayList<String>();
	String orderString = new String();
	int arduinoState = 0;
	int ledState = 0;
	int solisState = 0;
	int mode = 1;
	boolean stimStatus;
	boolean ledOn[] = {false, false, false, false};
	String colors[] = {"Blue","Green","Lime","Red"};
	String mouse = new String();
	String uni = new String();
	boolean readyToDeploy = false;

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
					strobeScreen frame = new strobeScreen();
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
	public strobeScreen() {
		setResizable(false);
		initComponents();
	}
	private void initComponents() {
		final OutputStream out = initializeArduino();
		setTitle("Strobe Settings");
		setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		setBounds(100, 100, 330, 262);
		contentPane = new JPanel();
		contentPane.setBorder(new EmptyBorder(5, 5, 5, 5));
		setContentPane(contentPane);
		
		JLabel lblOrder_1 = new JLabel("Strobe Order");
		lblOrder_1.setBounds(130, 61, 63, 14);
		
		JLabel lblLeds = new JLabel("LEDs");
		lblLeds.setBounds(41, 36, 23, 14);
		
		JButton btnDeploySettingsTo_1 = new JButton("Deploy Order to Arduino");
		btnDeploySettingsTo_1.setBounds(74, 193, 175, 23);
		btnDeploySettingsTo_1.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				List<String> s = orderList;
				try {
					writeJsonSettings(s);
					clearLeds(out);
					System.exit(0);
				} catch (Exception e1) {
					// TODO Auto-generated catch block
					System.out.println(e1.getMessage());
				}
			}

		});
		final JList list = new JList();
		final JLabel lblStrobeOrder = new JLabel();
		lblStrobeOrder.setBounds(264, 235, 0, 0);
		
		final JButton btnRed = new JButton("Red");
		btnRed.setBounds(10, 56, 84, 23);
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
		
		final JButton btnGreen = new JButton("Green");
		btnGreen.setBounds(10, 85, 84, 23);
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
		
		final JButton btnBlue = new JButton("Blue");
		btnBlue.setBounds(10, 114, 84, 23);
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
		
		final JButton btnSpeckle = new JButton("Lime");
		btnSpeckle.setBounds(10, 145, 84, 23);
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
		contentPane.add(lblStrobeOrder);
		contentPane.add(lblLeds);
		contentPane.add(lblOrder_1);;
		
		JLabel lblMode = new JLabel("Mode");
		lblMode.setHorizontalAlignment(SwingConstants.CENTER);
		lblMode.setBounds(193, 11, 46, 14);
		contentPane.add(lblMode);
		
		JLabel lblTestLights = new JLabel("Test LEDs");
		lblTestLights.setBounds(150, 36, 47, 14);
		contentPane.add(lblTestLights);
		
		JLabel lblSetOrder = new JLabel("Set Order");
		lblSetOrder.setBounds(237, 36, 58, 14);
		contentPane.add(lblSetOrder);
		list.setVisibleRowCount(4);
		list.setBounds(116, 81, 84, 72);
		contentPane.add(list);
		
		final JButton btnClear = new JButton("Clear");
		btnClear.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				updateStrobeOrder(arg0,list, out);
				btnBlue.setEnabled(true);
				btnGreen.setEnabled(true);
				btnRed.setEnabled(true);
				btnSpeckle.setEnabled(true);
			}
		});
		btnClear.setBounds(209, 100, 66, 23);
		contentPane.add(btnClear);
		
		final JSlider slider = new JSlider();
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
						final String[] orderArray = new String[orderList.size()];
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
		slider.setBounds(199, 36, 34, 14);
		contentPane.add(slider);
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
		final String[] orderArray = new String[orderList.size()];
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
		StringBuilder message = new StringBuilder("0000");
		message.setCharAt(i, '1');
		String msg = message.toString();
		try {
			//System.out.println("Sending "+ message +" to arduino");
			out.write(msg.getBytes());
			out.flush();
		} catch (IOException e1) {
			// TODO Auto-generated catch block
			e1.printStackTrace();
		}
	}
	
	private void writeJsonSettings(List<String> s) throws Exception {
		FileReader reader;
		if (s.size() < 1) {
			throw new Exception("The length of the Strobe Array must be greater than 0!");
		}
		reader = new FileReader("settings.json");
		JSONTokener tokener = new JSONTokener(reader);
		JSONObject settings = new JSONObject(tokener);
		reader.close();
		settings.put("strobe_order", s);
		settings.put("status", 4);
		PrintWriter out = new PrintWriter("settings.json");
		out.println(settings.toString());
		out.close();
	}
	
	private void clearLeds(OutputStream out) throws IOException {
		out.write("0000".getBytes());
		out.flush();
	}
}
