# yellow font: above cut-offs
# red font: below cut-offs

conc_tag = [25, 50, 75, 100]
vol_list_1 = [250*1.5, 500*1.5, 750*1.5, 1000*1.5]
vol_list_2 = [750*1.5, 500*1.5, 250*1.5, 0*1.5]

print(vol_list_1)

disp1_cutoff = 670
disp2_cutoff = 580


for i in range(len(vol_list_1)):

    x = vol_list_1[i]
    y = vol_list_2[i]

    if x < disp1_cutoff:
        # dispense_1d = controller.Dispense(nozzle=1, volume=x, wait_time=[0,3,12,3,0], motor_values=[-39000,80,-8530,80,39000], p = p1_default)
        print(f'From nozzle 1, dispensing \033[31m{x} \033[0muL  \n')
        #dispense_1d.run()
    else:
        #dispense_1d = controller.Dispense(nozzle=1, volume=x, wait_time=[0,3,12,3,0], motor_values=[-39000,80,-8530,80,39000], p = p_linear)
        print(f'From nozzle 1, dispensing \033[33m{x} \033[0muL  \n')
        #dispense_1d.run()

    if y < disp2_cutoff:
        #dispense_2d = controller.Dispense(nozzle=2, volume=y, wait_time=[0,3,12,3,0], motor_values=[-39000,80,-9230,80,39000], p = p2_default)
        print(f'From nozzle 2, dispensing \033[31m{y} \033[0muL  \n')
        #dispense_2d.run()
    else:
        #dispense_2d = controller.Dispense(nozzle=2, volume=y, wait_time=[0,3,12,3,0], motor_values=[-39000,80,-9230,80,39000], p = p_linear)
        print(f'From nozzle 2, dispensing \033[33m{y} \033[0muL  \n')
        #dispense_2d.run()




