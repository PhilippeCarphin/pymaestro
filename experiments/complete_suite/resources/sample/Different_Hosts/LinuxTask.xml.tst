<NODE_RESOURCES>
  <!-- batch resource definition
  supported attributes: machine, queue, memory, mpi, wallclock, catchup, cpu, soumet_args
  -->
  <BATCH machine="${FRONTEND}" memory="5G" mpi="1" wallclock="3" catchup="4" cpu="1" cpu_multiplier="1" soumet_args="-tmpfs 4000M -shell /bin/bash" />
  <ABORT_ACTION name="rerun" /> 

</NODE_RESOURCES> 
