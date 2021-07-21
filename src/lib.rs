#[no_mangle]
pub unsafe extern fn tick(massives: *const Massive, len: usize)->Result{ //Performs one step of the simulation
    
    let mut massives = core::slice::from_raw_parts(massives, len).to_vec().to_owned(); //Unsafe code: take length and pointer to area of memory and construct the massives vector from it

    let mut to_remove = vec![]; //Declare empty vectors for handling collided massives
    let mut to_push = vec![];

    for i_p in 0..len{ //Iterate through each pair of massive
        for j_p in 0..len{
            if i_p != j_p{
                let j = massives[j_p];
                let mut i = &mut massives[i_p];
                let delta_x = j.pos_x - i.pos_x;
                let delta_y = j.pos_y - i.pos_y;
                
                i.vel_x += delta_x * f64::powf(delta_x * delta_x + delta_y * delta_y,-1.5) * j.mass; //The meat of the n-body simulation
                i.vel_y += delta_y * f64::powf(delta_x * delta_x + delta_y * delta_y,-1.5) * j.mass; //Physics

                if ! (to_remove.contains(&i_p) & to_remove.contains(&j_p)) { //As long as we haven't already checked this pair...
                    let delta_x = j.pos_x - i.pos_x;
                    let delta_y = j.pos_y - i.pos_y;
                    let dist = f64::sqrt((delta_x * delta_x) + (delta_y * delta_y)); 

                
                    if dist < (j.radius + i.radius) as f64{ //If distance between massives is less than combined radii (massives touching)

                        to_remove.push(i_p); //Remember to remove these from the list later (not now, avoid manipulating list as we are iterating on it)
                        to_remove.push(j_p);

                        let newp = collide(&i, &j); //Calculate new massive from collision
                        to_push.push(newp);

                    }
                }

            }
        }
    }


    
    
    if to_push.len() > 0 { //Remove massives marked for removal, add new massives

        to_remove.sort();
        to_remove.dedup();

        if to_remove.len() == massives.len(){
            massives = vec![];
        }else if to_remove.len() > 0{
            to_remove.sort();
            to_remove.dedup();
            for i in 0..to_remove.len() {
                massives.remove(to_remove[to_remove.len()-i-1]);
            }
        }
        massives.append(&mut to_push);
    }

    let mut has_nan = false; //If the data we're pointing into is junk
    
    for i in massives.iter_mut(){
        
        i.pos_x += i.vel_x; //Apply velocities to positions
        i.pos_y += i.vel_y; //Physics
    
        if f64::is_nan(i.pos_x) { //Check for junk data
            has_nan = true;
        };

    }

    Result{pointer: massives.as_mut_ptr(), length: massives.len(), is_broken: has_nan} //Return deconstructed slice and broken data indicator
}

pub extern fn collide(massive1: &Massive, massive2: &Massive)->Massive{ //Takes 2 massives, calculates resulting massive

    //To find new radius, find area of both massives, sum them, and derive radius from this new area
    let summed_area = (((massive1.radius) * (massive1.radius)) as f64 * 3.141) + (((massive2.radius) * (massive2.radius)) as f64 * 3.141);
    let new_radius = f64::sqrt(summed_area / 3.141) as u32;


    Massive{
        mass: massive1.mass + massive2.mass,
        vel_x: (massive1.mass * massive1.vel_x + massive2.mass * massive2.vel_x) / (massive1.mass + massive2.mass), //weighted average by mass
        vel_y: (massive1.mass * massive1.vel_x + massive2.mass * massive2.vel_x) / (massive1.mass + massive2.mass),
        pos_x: (massive1.pos_x * massive1.radius as f64 + massive2.pos_x * massive2.radius as f64 ) / (massive1.radius + massive2.radius) as f64, //weighted average by radius
        pos_y: (massive2.pos_y * massive1.radius as f64 + massive2.pos_y * massive2.radius as f64) / (massive1.radius + massive2.radius) as f64,
        radius: new_radius
    }
}


//Structs
#[repr(C)]
#[derive(Debug, Copy, Clone)]
pub struct Massive { //The 'body' part of an n-body simulation. Values needed to display or simulate masses
    mass: f64,
    vel_x: f64,
    vel_y: f64,
    pos_x: f64,
    pos_y: f64,
    radius: u32
}

#[repr(C)]
#[derive(Debug, Copy, Clone)]
pub struct Result { //Struct to return to python program. Contains raw part for list/slice, and an indicator on if data is junk
    pointer: *const Massive,
    length: usize,
    is_broken: bool,
}

