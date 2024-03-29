import { Component, TemplateRef, ViewChild } from '@angular/core';
import { MatDialog, MatDialogRef } from '@angular/material/dialog';
import { MermaidAPI } from 'ngx-markdown';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Inject } from '@angular/core';
import { DataService } from '../services/app.data.service';

@Component({
  selector: 'app-library-element',
  templateUrl: './library-element.component.html',
  styleUrls: ['./library-element.component.css']
})
export class LibraryElementComponent {

  options: MermaidAPI.Config = {
    fontFamily: '"trebuchet ms", verdana, arial, sans-serif',
    logLevel: MermaidAPI.LogLevel.Info,
    theme: MermaidAPI.Theme.Dark
  };

  descriptionFilePath: string;
  dataFilePath: string;
  elementTitle: string;

  constructor(public dataService: DataService, public dialog: MatDialog, public dialogRef: MatDialogRef<LibraryElementComponent>, @Inject(MAT_DIALOG_DATA) public data: any) {
    this.descriptionFilePath = this.data["md_file_path"];
    this.dataFilePath = this.data["data_file_path"];
    this.elementTitle = this.data["title"]
    console.log(this.descriptionFilePath)
    console.log(this.dataFilePath)
  }

  fillConf() {

    this.dataService.setConfigurationData({
      "drone_0": {
          "Processes": [
              {
                  "PID": 1056,
                  "PPID": 1,
                  "Process Name": "drone_comms",
                  "Known Process": "ProcessName.UNKNOWN",
                  "Username": "drone_user",
                  "Path": "/ usr / sbin",
                  "Known Path": "Path.UNKNOWN",
                  "Connections": [
                      {
                          "local_port": 8888,
                          "local_address": "0.0.0.0",
                          "Transport Protocol": "UNKNOWN"
                      }
                  ],
                  "Process Type": "UNKNOWN"
              },
              {
                  "PID": 1091,
                  "PPID": 1,
                  "Process Name": "sshd",
                  "Known Process": "ProcessName.SSHD",
                  "Username": "root",
                  "Path": "/ usr / sbin",
                  "Known Path": "Path.UNKNOWN",
                  "Connections": [
                      {
                          "local_port": 22,
                          "local_address": "0.0.0.0",
                          "Transport Protocol": "UNKNOWN"
                      }
                  ],
                  "Process Type": "SSH"
              },
              {
                  "PID": 1094,
                  "Process Name": "blue_drone_session",
                  "Known Process": "ProcessName.UNKNOWN",
                  "Username": "root",
                  "Process Type": "UNKNOWN"
              },
              {
                  "PID": 1100,
                  "Process Name": "green_session",
                  "Known Process": "ProcessName.UNKNOWN",
                  "Username": "hardware",
                  "Process Type": "UNKNOWN"
              }
          ],
          "Interface": [
              {
                  "Interface Name": "wlan0",
                  "IP Address": "10.0.222.210",
                  "Subnet": "10.0.222.208/28"
              }
          ],
          "Sessions": [
              {
                  "Username": "root",
                  "ID": 0,
                  "Timeout": 0,
                  "PID": 1094,
                  "Type": "BLUE_DRONE_SESSION",
                  "Agent": "blue_agent_0"
              },
              {
                  "Username": "hardware",
                  "ID": 0,
                  "Timeout": 0,
                  "PID": 1100,
                  "Type": "GREY_SESSION",
                  "Agent": "green_agent_0"
              }
          ],
          "User Info": [
              {
                  "Username": "root",
                  "Groups": [
                      {
                          "GID": 0
                      }
                  ]
              },
              {
                  "Username": "drone_user",
                  "Groups": [
                      {
                          "GID": 0
                      }
                  ]
              }
          ],
          "System info": {
              "Hostname": "drone_0",
              "OSType": "LINUX",
              "OSDistribution": "DRONE_LINUX",
              "OSVersion": "UNKNOWN",
              "Architecture": "Architecture.UNKNOWN",
              "position": [
                  50.01345383510313,
                  42.26985386972709
              ]
          }
      },
      "drone_1": {
          "Processes": [
              {
                  "PID": 1056,
                  "PPID": 1,
                  "Process Name": "drone_comms",
                  "Known Process": "ProcessName.UNKNOWN",
                  "Username": "drone_user",
                  "Path": "/ usr / sbin",
                  "Known Path": "Path.UNKNOWN",
                  "Connections": [
                      {
                          "local_port": 8888,
                          "local_address": "0.0.0.0",
                          "Transport Protocol": "UNKNOWN"
                      }
                  ],
                  "Process Type": "UNKNOWN"
              },
              {
                  "PID": 1091,
                  "PPID": 1,
                  "Process Name": "sshd",
                  "Known Process": "ProcessName.SSHD",
                  "Username": "root",
                  "Path": "/ usr / sbin",
                  "Known Path": "Path.UNKNOWN",
                  "Connections": [
                      {
                          "local_port": 22,
                          "local_address": "0.0.0.0",
                          "Transport Protocol": "UNKNOWN"
                      }
                  ],
                  "Process Type": "SSH"
              },
              {
                  "PID": 1092,
                  "Process Name": "blue_drone_session",
                  "Known Process": "ProcessName.UNKNOWN",
                  "Username": "root",
                  "Process Type": "UNKNOWN"
              },
              {
                  "PID": 1094,
                  "Process Name": "green_session",
                  "Known Process": "ProcessName.UNKNOWN",
                  "Username": "hardware",
                  "Process Type": "UNKNOWN"
              }
          ],
          "Interface": [
              {
                  "Interface Name": "wlan0",
                  "IP Address": "10.0.222.209",
                  "Subnet": "10.0.222.208/28"
              }
          ],
          "Sessions": [
              {
                  "Username": "root",
                  "ID": 0,
                  "Timeout": 0,
                  "PID": 1092,
                  "Type": "BLUE_DRONE_SESSION",
                  "Agent": "blue_agent_1"
              },
              {
                  "Username": "hardware",
                  "ID": 0,
                  "Timeout": 0,
                  "PID": 1094,
                  "Type": "GREY_SESSION",
                  "Agent": "green_agent_1"
              }
          ],
          "User Info": [
              {
                  "Username": "root",
                  "Groups": [
                      {
                          "GID": 0
                      }
                  ]
              },
              {
                  "Username": "drone_user",
                  "Groups": [
                      {
                          "GID": 0
                      }
                  ]
              }
          ],
          "System info": {
              "Hostname": "drone_1",
              "OSType": "LINUX",
              "OSDistribution": "DRONE_LINUX",
              "OSVersion": "UNKNOWN",
              "Architecture": "Architecture.UNKNOWN",
              "position": [
                  60.14720776781141,
                  55.36159708474876
              ]
          }
      },
      "drone_2": {
          "Processes": [
              {
                  "PID": 1056,
                  "PPID": 1,
                  "Process Name": "drone_comms",
                  "Known Process": "ProcessName.UNKNOWN",
                  "Username": "drone_user",
                  "Path": "/ usr / sbin",
                  "Known Path": "Path.UNKNOWN",
                  "Connections": [
                      {
                          "local_port": 8888,
                          "local_address": "0.0.0.0",
                          "Transport Protocol": "UNKNOWN"
                      }
                  ],
                  "Process Type": "UNKNOWN"
              },
              {
                  "PID": 1091,
                  "PPID": 1,
                  "Process Name": "sshd",
                  "Known Process": "ProcessName.SSHD",
                  "Username": "root",
                  "Path": "/ usr / sbin",
                  "Known Path": "Path.UNKNOWN",
                  "Connections": [
                      {
                          "local_port": 22,
                          "local_address": "0.0.0.0",
                          "Transport Protocol": "UNKNOWN"
                      }
                  ],
                  "Process Type": "SSH"
              },
              {
                  "PID": 1092,
                  "Process Name": "blue_drone_session",
                  "Known Process": "ProcessName.UNKNOWN",
                  "Username": "root",
                  "Process Type": "UNKNOWN"
              },
              {
                  "PID": 1099,
                  "Process Name": "green_session",
                  "Known Process": "ProcessName.UNKNOWN",
                  "Username": "hardware",
                  "Process Type": "UNKNOWN"
              }
          ],
          "Interface": [
              {
                  "Interface Name": "wlan0",
                  "IP Address": "10.0.222.220",
                  "Subnet": "10.0.222.208/28"
              }
          ],
          "Sessions": [
              {
                  "Username": "root",
                  "ID": 0,
                  "Timeout": 0,
                  "PID": 1092,
                  "Type": "BLUE_DRONE_SESSION",
                  "Agent": "blue_agent_2"
              },
              {
                  "Username": "hardware",
                  "ID": 0,
                  "Timeout": 0,
                  "PID": 1099,
                  "Type": "GREY_SESSION",
                  "Agent": "green_agent_2"
              }
          ],
          "User Info": [
              {
                  "Username": "root",
                  "Groups": [
                      {
                          "GID": 0
                      }
                  ]
              },
              {
                  "Username": "drone_user",
                  "Groups": [
                      {
                          "GID": 0
                      }
                  ]
              }
          ],
          "System info": {
              "Hostname": "drone_2",
              "OSType": "LINUX",
              "OSDistribution": "DRONE_LINUX",
              "OSVersion": "UNKNOWN",
              "Architecture": "Architecture.UNKNOWN",
              "position": [
                  30.191651136741115,
                  71.92957421950157
              ]
          }
      },
      "drone_3": {
          "Processes": [
              {
                  "PID": 1056,
                  "PPID": 1,
                  "Process Name": "drone_comms",
                  "Known Process": "ProcessName.UNKNOWN",
                  "Username": "drone_user",
                  "Path": "/ usr / sbin",
                  "Known Path": "Path.UNKNOWN",
                  "Connections": [
                      {
                          "local_port": 8888,
                          "local_address": "0.0.0.0",
                          "Transport Protocol": "UNKNOWN"
                      }
                  ],
                  "Process Type": "UNKNOWN"
              },
              {
                  "PID": 1091,
                  "PPID": 1,
                  "Process Name": "sshd",
                  "Known Process": "ProcessName.SSHD",
                  "Username": "root",
                  "Path": "/ usr / sbin",
                  "Known Path": "Path.UNKNOWN",
                  "Connections": [
                      {
                          "local_port": 22,
                          "local_address": "0.0.0.0",
                          "Transport Protocol": "UNKNOWN"
                      }
                  ],
                  "Process Type": "SSH"
              },
              {
                  "PID": 1094,
                  "Process Name": "blue_drone_session",
                  "Known Process": "ProcessName.UNKNOWN",
                  "Username": "root",
                  "Process Type": "UNKNOWN"
              },
              {
                  "PID": 1098,
                  "Process Name": "green_session",
                  "Known Process": "ProcessName.UNKNOWN",
                  "Username": "hardware",
                  "Process Type": "UNKNOWN"
              }
          ],
          "Interface": [
              {
                  "Interface Name": "wlan0",
                  "IP Address": "10.0.222.215",
                  "Subnet": "10.0.222.208/28"
              }
          ],
          "Sessions": [
              {
                  "Username": "root",
                  "ID": 0,
                  "Timeout": 0,
                  "PID": 1094,
                  "Type": "BLUE_DRONE_SESSION",
                  "Agent": "blue_agent_3"
              },
              {
                  "Username": "hardware",
                  "ID": 0,
                  "Timeout": 0,
                  "PID": 1098,
                  "Type": "GREY_SESSION",
                  "Agent": "green_agent_3"
              }
          ],
          "User Info": [
              {
                  "Username": "root",
                  "Groups": [
                      {
                          "GID": 0
                      }
                  ]
              },
              {
                  "Username": "drone_user",
                  "Groups": [
                      {
                          "GID": 0
                      }
                  ]
              }
          ],
          "System info": {
              "Hostname": "drone_3",
              "OSType": "LINUX",
              "OSDistribution": "DRONE_LINUX",
              "OSVersion": "UNKNOWN",
              "Architecture": "Architecture.UNKNOWN",
              "position": [
                  16.61232148052927,
                  56.02232834768942
              ]
          }
      },
      "drone_4": {
          "Processes": [
              {
                  "PID": 1056,
                  "PPID": 1,
                  "Process Name": "drone_comms",
                  "Known Process": "ProcessName.UNKNOWN",
                  "Username": "drone_user",
                  "Path": "/ usr / sbin",
                  "Known Path": "Path.UNKNOWN",
                  "Connections": [
                      {
                          "local_port": 8888,
                          "local_address": "0.0.0.0",
                          "Transport Protocol": "UNKNOWN"
                      }
                  ],
                  "Process Type": "UNKNOWN"
              },
              {
                  "PID": 1091,
                  "PPID": 1,
                  "Process Name": "sshd",
                  "Known Process": "ProcessName.SSHD",
                  "Username": "root",
                  "Path": "/ usr / sbin",
                  "Known Path": "Path.UNKNOWN",
                  "Connections": [
                      {
                          "local_port": 22,
                          "local_address": "0.0.0.0",
                          "Transport Protocol": "UNKNOWN"
                      }
                  ],
                  "Process Type": "SSH"
              },
              {
                  "PID": 1092,
                  "Process Name": "blue_drone_session",
                  "Known Process": "ProcessName.UNKNOWN",
                  "Username": "root",
                  "Process Type": "UNKNOWN"
              },
              {
                  "PID": 1101,
                  "Process Name": "green_session",
                  "Known Process": "ProcessName.UNKNOWN",
                  "Username": "hardware",
                  "Process Type": "UNKNOWN"
              }
          ],
          "Interface": [
              {
                  "Interface Name": "wlan0",
                  "IP Address": "10.0.222.221",
                  "Subnet": "10.0.222.208/28"
              }
          ],
          "Sessions": [
              {
                  "Username": "root",
                  "ID": 0,
                  "Timeout": 0,
                  "PID": 1092,
                  "Type": "BLUE_DRONE_SESSION",
                  "Agent": "blue_agent_4"
              },
              {
                  "Username": "hardware",
                  "ID": 0,
                  "Timeout": 0,
                  "PID": 1101,
                  "Type": "GREY_SESSION",
                  "Agent": "green_agent_4"
              }
          ],
          "User Info": [
              {
                  "Username": "root",
                  "Groups": [
                      {
                          "GID": 0
                      }
                  ]
              },
              {
                  "Username": "drone_user",
                  "Groups": [
                      {
                          "GID": 0
                      }
                  ]
              }
          ],
          "System info": {
              "Hostname": "drone_4",
              "OSType": "LINUX",
              "OSDistribution": "DRONE_LINUX",
              "OSVersion": "UNKNOWN",
              "Architecture": "Architecture.UNKNOWN",
              "position": [
                  95.2142689708642,
                  30.71426903330776
              ]
          }
      },
      "drone_5": {
          "Processes": [
              {
                  "PID": 1056,
                  "PPID": 1,
                  "Process Name": "drone_comms",
                  "Known Process": "ProcessName.UNKNOWN",
                  "Username": "drone_user",
                  "Path": "/ usr / sbin",
                  "Known Path": "Path.UNKNOWN",
                  "Connections": [
                      {
                          "local_port": 8888,
                          "local_address": "0.0.0.0",
                          "Transport Protocol": "UNKNOWN"
                      }
                  ],
                  "Process Type": "UNKNOWN"
              },
              {
                  "PID": 1091,
                  "PPID": 1,
                  "Process Name": "sshd",
                  "Known Process": "ProcessName.SSHD",
                  "Username": "root",
                  "Path": "/ usr / sbin",
                  "Known Path": "Path.UNKNOWN",
                  "Connections": [
                      {
                          "local_port": 22,
                          "local_address": "0.0.0.0",
                          "Transport Protocol": "UNKNOWN"
                      }
                  ],
                  "Process Type": "SSH"
              },
              {
                  "PID": 1095,
                  "Process Name": "blue_drone_session",
                  "Known Process": "ProcessName.UNKNOWN",
                  "Username": "root",
                  "Process Type": "UNKNOWN"
              },
              {
                  "PID": 1101,
                  "Process Name": "green_session",
                  "Known Process": "ProcessName.UNKNOWN",
                  "Username": "hardware",
                  "Process Type": "UNKNOWN"
              }
          ],
          "Interface": [
              {
                  "Interface Name": "wlan0",
                  "IP Address": "10.0.222.218",
                  "Subnet": "10.0.222.208/28"
              }
          ],
          "Sessions": [
              {
                  "Username": "root",
                  "ID": 0,
                  "Timeout": 0,
                  "PID": 1095,
                  "Type": "BLUE_DRONE_SESSION",
                  "Agent": "blue_agent_5"
              },
              {
                  "Username": "hardware",
                  "ID": 0,
                  "Timeout": 0,
                  "PID": 1101,
                  "Type": "GREY_SESSION",
                  "Agent": "green_agent_5"
              }
          ],
          "User Info": [
              {
                  "Username": "root",
                  "Groups": [
                      {
                          "GID": 0
                      }
                  ]
              },
              {
                  "Username": "drone_user",
                  "Groups": [
                      {
                          "GID": 0
                      }
                  ]
              }
          ],
          "System info": {
              "Hostname": "drone_5",
              "OSType": "LINUX",
              "OSDistribution": "DRONE_LINUX",
              "OSVersion": "UNKNOWN",
              "Architecture": "Architecture.UNKNOWN",
              "position": [
                  12.069277853381294,
                  24.712105864300504
              ]
          }
      },
      "drone_6": {
          "Processes": [
              {
                  "PID": 1056,
                  "PPID": 1,
                  "Process Name": "drone_comms",
                  "Known Process": "ProcessName.UNKNOWN",
                  "Username": "drone_user",
                  "Path": "/ usr / sbin",
                  "Known Path": "Path.UNKNOWN",
                  "Connections": [
                      {
                          "local_port": 8888,
                          "local_address": "0.0.0.0",
                          "Transport Protocol": "UNKNOWN"
                      }
                  ],
                  "Process Type": "UNKNOWN"
              },
              {
                  "PID": 1091,
                  "PPID": 1,
                  "Process Name": "sshd",
                  "Known Process": "ProcessName.SSHD",
                  "Username": "root",
                  "Path": "/ usr / sbin",
                  "Known Path": "Path.UNKNOWN",
                  "Connections": [
                      {
                          "local_port": 22,
                          "local_address": "0.0.0.0",
                          "Transport Protocol": "UNKNOWN"
                      }
                  ],
                  "Process Type": "SSH"
              },
              {
                  "PID": 1097,
                  "Process Name": "blue_drone_session",
                  "Known Process": "ProcessName.UNKNOWN",
                  "Username": "root",
                  "Process Type": "UNKNOWN"
              },
              {
                  "PID": 1104,
                  "Process Name": "green_session",
                  "Known Process": "ProcessName.UNKNOWN",
                  "Username": "hardware",
                  "Process Type": "UNKNOWN"
              }
          ],
          "Interface": [
              {
                  "Interface Name": "wlan0",
                  "IP Address": "10.0.222.216",
                  "Subnet": "10.0.222.208/28"
              }
          ],
          "Sessions": [
              {
                  "Username": "root",
                  "ID": 0,
                  "Timeout": 0,
                  "PID": 1097,
                  "Type": "BLUE_DRONE_SESSION",
                  "Agent": "blue_agent_6"
              },
              {
                  "Username": "hardware",
                  "ID": 0,
                  "Timeout": 0,
                  "PID": 1104,
                  "Type": "GREY_SESSION",
                  "Agent": "green_agent_6"
              }
          ],
          "User Info": [
              {
                  "Username": "root",
                  "Groups": [
                      {
                          "GID": 0
                      }
                  ]
              },
              {
                  "Username": "drone_user",
                  "Groups": [
                      {
                          "GID": 0
                      }
                  ]
              }
          ],
          "System info": {
              "Hostname": "drone_6",
              "OSType": "LINUX",
              "OSDistribution": "DRONE_LINUX",
              "OSVersion": "UNKNOWN",
              "Architecture": "Architecture.UNKNOWN",
              "position": [
                  95.50265638069109,
                  57.2278339476445
              ]
          }
      },
      "drone_7": {
          "Processes": [
              {
                  "PID": 1056,
                  "PPID": 1,
                  "Process Name": "drone_comms",
                  "Known Process": "ProcessName.UNKNOWN",
                  "Username": "drone_user",
                  "Path": "/ usr / sbin",
                  "Known Path": "Path.UNKNOWN",
                  "Connections": [
                      {
                          "local_port": 8888,
                          "local_address": "0.0.0.0",
                          "Transport Protocol": "UNKNOWN"
                      }
                  ],
                  "Process Type": "UNKNOWN"
              },
              {
                  "PID": 1091,
                  "PPID": 1,
                  "Process Name": "sshd",
                  "Known Process": "ProcessName.SSHD",
                  "Username": "root",
                  "Path": "/ usr / sbin",
                  "Known Path": "Path.UNKNOWN",
                  "Connections": [
                      {
                          "local_port": 22,
                          "local_address": "0.0.0.0",
                          "Transport Protocol": "UNKNOWN"
                      }
                  ],
                  "Process Type": "SSH"
              },
              {
                  "PID": 1096,
                  "Process Name": "blue_drone_session",
                  "Known Process": "ProcessName.UNKNOWN",
                  "Username": "root",
                  "Process Type": "UNKNOWN"
              },
              {
                  "PID": 1100,
                  "Process Name": "green_session",
                  "Known Process": "ProcessName.UNKNOWN",
                  "Username": "hardware",
                  "Process Type": "UNKNOWN"
              }
          ],
          "Interface": [
              {
                  "Interface Name": "wlan0",
                  "IP Address": "10.0.222.219",
                  "Subnet": "10.0.222.208/28"
              }
          ],
          "Sessions": [
              {
                  "Username": "root",
                  "ID": 0,
                  "Timeout": 0,
                  "PID": 1096,
                  "Type": "BLUE_DRONE_SESSION",
                  "Agent": "blue_agent_7"
              },
              {
                  "Username": "hardware",
                  "ID": 0,
                  "Timeout": 0,
                  "PID": 1100,
                  "Type": "GREY_SESSION",
                  "Agent": "green_agent_7"
              }
          ],
          "User Info": [
              {
                  "Username": "root",
                  "Groups": [
                      {
                          "GID": 0
                      }
                  ]
              },
              {
                  "Username": "drone_user",
                  "Groups": [
                      {
                          "GID": 0
                      }
                  ]
              }
          ],
          "System info": {
              "Hostname": "drone_7",
              "OSType": "LINUX",
              "OSDistribution": "DRONE_LINUX",
              "OSVersion": "UNKNOWN",
              "Architecture": "Architecture.UNKNOWN",
              "position": [
                  86.27885722156695,
                  76.77883471718054
              ]
          }
      }
  })

  }

}
