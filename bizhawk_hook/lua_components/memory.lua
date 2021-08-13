---------------------------------------------------------
-- The Lua side of things would not have been possible --
-- if it weren't for the help of one lovely individual --
--                                                     --
-- Tumn                                                --
--   * Matrix: @autumn:raincloud.dev                   --
--   * GitHub: github.com/rosemash                     --
---------------------------------------------------------

address, port = "127.0.0.1", 16154

---------------------------------------------------------
-- # HOW TO USE                                        --
--                                                     --
-- Requests can be made by connecting to the socket    --
-- at the specified address and port and sending       --
-- a message following the pattern below.              --
--                                                     --
--    OBS! Every request requires a new connection.    --
--                                                     --
--                                                     --
-- Pattern:  DOMN/ADDR/TSLE/VLUE                       --
--                                                     --
-- DOMN  - Memory domain                               --
-- ADDR  - Address                                     --
-- TSLE--.-------------------.                         --
--       Type:               Signage:                  --
--       | * [b]yte            * [u]nsigned            --
--       | * [i]nteger         * [s]igned              --
--       | * [f]loat                                   --
--       |                                             --
--       .-------------------.                         --
--       Length              Endianness                --
--         * [1] byte          * [l]ittle endian       --
--         * [2] bytes         * [b]ig endian          --
--         * [3] bytes                                 --
--         * [4] bytes                                 --
--                                                     --
--  VLUE  - Integer or float, ex. 12 or -1.2           --
--                                                     --
--                                                     --
--  # EXAMPLES                                         --
--                                                     --
--   VRAM/11423051/iu4b/23                             --
--     Write (23) to (11423051) in (VRAM)              --
--       an [i]nteger, [u]nsigned,                     --
--       [4] bytes long and [b]ig endian               --
--                                                     --
--   WRAM/21512962/fs2l/                               --
--     Read from (21512962) in (WRAM)                  --
--       a [f]loat, [s]igned,                          --
--       [2] bytes long and [l]ittle endian            --
--                                                     --
---------------------------------------------------------


-- Include necessary socket modules using a hack

local version = _VERSION:match("%d+%.%d+")

package.path = 'lua_modules/share/lua/'
			.. version
			.. '/?.lua;lua_modules/share/lua/'
			.. version
			.. '/?/init.lua;'
			.. package.path

package.cpath = 'lua_modules/lib/lua/'
			.. version
			.. '/?.so;'
			.. package.cpath


-- Import modules and set up socket connection

socket = require("socket")
copas = require("copas")

server = socket.bind(address, port)


-- Response codes
rcodes = {
	WRITTEN = 0;  -- Successfully wrote to memory
	BYTE    = 1;  -- Successfully read byte
	INTEGER = 2;  -- Successfully read integer
	FLOAT   = 3;  -- Successfully read float
	ERROR   = 4;  -- Generic error
}

local function response(code, message)
	return code .. '_' .. message
end


local function handleRequest(data)
	-- Handle incoming requests for reading from
	-- and writing to memory with the BizHawk emulator
	
	domain, address, type, signage, length, endianness, value
        = data:match('^([%w%s]*)%/(%d+)%/([bif])([us])([1234])([lb])%/(-?%d*%.?%d*)$')

	
	-- Use default domain if none is provided
	if domain == "" then
		domain = nil
	end
		
	-- Convert address to integer
	address = tonumber(address)


	-- [ READ ]
	if not value then

		-- [ BYTE ]
		if type == 'b' then
			return response(
				rcodes.BYTE,
				memory.readbyte(address, domain)
			)
		end

		
		-- [ INTEGER ]
		if type == 'i' then
			
			-- [ UNSIGNED ]
			if signage == 'u' then
				
				-- [ 1 BYTE ]
				if length == '1' then
					return response(
						rcodes.INTEGER,
						memory.read_u8(address, domain)
					)
				end

				-- [ LITTLE ENDIAN ]
				if endianness == 'l' then
					
					-- [ 2 BYTE ]
					if length == '2' then
						return response(
							rcodes.INTEGER,
							memory.read_u16_le(address, domain)
						)
						
					-- [ 3 BYTE ]
					elseif length == '3' then
						return response(
							rcodes.INTEGER,
							memory.read_u24_le(address, domain)
						)
						
					-- [ 4 BYTE ]
					elseif length == '4' then
						return response(
							rcodes.INTEGER,
							memory.read_u32_le(address, domain)
						)
					end
				end

				-- [ BIG ENDIAN ]
				if endianness == 'b' then

					-- [ 2 BYTE ]
					if length == '2' then
						return response(
							rcodes.INTEGER,
							memory.read_u16_be(address, domain)
						)

					-- [ 3 BYTE ]
					elseif length == '3' then
						return response(
							rcodes.INTEGER,
							memory.read_u24_be(address, domain)
						)

					-- [ 4 BYTE ]
					elseif length == '4' then
						return response(
							rcodes.INTEGER,
							memory.read_u32_be(address, domain)
						)
					end
				end
			end

			-- [ SIGNED ]
			if signage == 's' then
				
				-- [ 1 BYTE ]
				if length == '1' then
					return response(
						rcodes.INTEGER,
						memory.read_s8(address, domain)
					)
				end

				-- [ LITTLE ENDIAN ]
				if endianness == 'l' then
					
					-- [ 2 BYTE ]
					if length == '2' then
						return response(
							rcodes.INTEGER,
							memory.read_s16_le(address, domain)
						)
						
					-- [ 3 BYTE ]
					elseif length == '3' then
						return response(
							rcodes.INTEGER,
							memory.read_s24_le(address, domain)
						)
						
					-- [ 4 BYTE ]
					elseif length == '4' then
						return response(
							rcodes.INTEGER,
							memory.read_s32_le(address, domain)
						)

					end
				end

				-- [ BIG ENDIAN ]
				if endianness == 'b' then

					-- [ 2 BYTE ]
					if length == '2' then
						return response(
							rcodes.INTEGER,
							memory.read_s16_be(address, domain)
						)

					-- [ 3 BYTE ]
					elseif length == '3' then
						return response(
							rcodes.INTEGER,
							memory.read_s24_be(address, domain)
						)

					-- [ 4 BYTE ]
					elseif length == '4' then
						return response(
							rcodes.INTEGER,
							memory.read_s32_be(address, domain)
						)

					end
				end
			end
		end

		-- [ FLOAT ]
		if type == 'f' then

			-- Whether the value is big endian or not
			bigendian = endianness == 'b'

			return response(
				rcodes.FLOAT,
				memory.readfloat(address, bigendian, domain)
			)
		end

	-- [ WRITE ]
	else
		
		-- Convert value to number
		value = tonumber(value)


		-- [ BYTE ]
		if type == 'b' then
			return response(
				rcodes.WRITTEN,
				memory.writebyte(address, value, domain)
			)
		end

		
		-- [ INTEGER ]
		if type == 'i' then
			
			-- [ UNSIGNED ]
			if signage == 'u' then
				
				-- [ 1 BYTE ]
				if length == '1' then
					return response(
						rcodes.WRITTEN,
						memory.write_u8(address, value, domain)
					)
				end

				-- [ LITTLE ENDIAN ]
				if endianness == 'l' then
					
					-- [ 2 BYTE ]
					if length == '2' then
						return response(
							rcodes.WRITTEN,
							memory.write_u16_le(address, value, domain)
						)
						
					-- [ 3 BYTE ]
					elseif length == '3' then
						return response(
							rcodes.WRITTEN,
							memory.write_u24_le(address, value, domain)
						)
						
					-- [ 4 BYTE ]
					elseif length == '4' then
						return response(
							rcodes.WRITTEN,
							memory.write_u32_le(address, value, domain)
						)
					end
				end

				-- [ BIG ENDIAN ]
				if endianness == 'b' then

					-- [ 2 BYTE ]
					if length == '2' then
						return response(
							rcodes.WRITTEN,
							memory.write_u16_be(address, value, domain)
						)

					-- [ 3 BYTE ]
					elseif length == '3' then
						return response(
							rcodes.WRITTEN,
							memory.write_u24_be(address, value, domain)
						)

					-- [ 4 BYTE ]
					elseif length == '4' then
						return response(
							rcodes.WRITTEN,
							memory.write_u32_be(address, value, domain)
						)
					end
				end
			end

			-- [ SIGNED ]
			if signage == 's' then
				
				-- [ 1 BYTE ]
				if length == '1' then
					return response(
						rcodes.WRITTEN,
						memory.write_s8(address, value, domain)
					)
				end

				-- [ LITTLE ENDIAN ]
				if endianness == 'l' then
					
					-- [ 2 BYTE ]
					if length == '2' then
						return response(
							rcodes.WRITTEN,
							memory.write_s16_le(address, value, domain)
						)
						
					-- [ 3 BYTE ]
					elseif length == '3' then
						return response(
							rcodes.WRITTEN,
							memory.write_s24_le(address, value, domain)
						)
						
					-- [ 4 BYTE ]
					elseif length == '4' then
						return response(
							rcodes.WRITTEN,
							memory.write_s32_le(address, value, domain)
						)
					end
				end

				-- [ BIG ENDIAN ]
				if endianness == 'b' then

					-- [ 2 BYTE ]
					if length == '2' then
						return response(
							rcodes.WRITTEN,
							memory.write_s16_be(address, value, domain)
						)

					-- [ 3 BYTE ]
					elseif length == '3' then
						return response(
							rcodes.WRITTEN,
							memory.write_s24_be(address, value, domain)
						)

					-- [ 4 BYTE ]
					elseif length == '4' then
						return response(
							rcodes.WRITTEN,
							memory.write_s32_be(address, value, domain)
						)
					end
				end
			end
		end

		-- [ FLOAT ]
		if type == 'f' then
			
			-- Whether the value is big endian or not
			bigendian = endianness == 'b'

			return response(
				rcodes.WRITTEN,
				memory.writefloat(address, value, bigendian, domain)
			)
		end
	end


	-- If nothing is matched,
	-- let the client know that something's gone wrong
	return response(rcodes.ERROR, 'INVALID_REQUEST')
end

local function clientHandler(client)
	-- Reads data until client is disconnected
	-- and processes the data with handleRequest

	local data = ""

	while true do
		-- Read 1 byte at a time
		chunk, errmsg = client:receive(1)
		
		-- Quit reading if an error has occured
		-- or no data was received
		if not chunk then
			if errmsg == 'timeout' then
				break
			end
			
			print(('Socket error: %s'):format(errmsg))
			return
		end

		-- Append new byte to data
		data = data .. chunk
	end


	if not data then return end

	-- Handle the request
	-- and formulate a response
	response = handleRequest(data)

	if not response then return end

	-- Make sure response is string
	-- and send back response to client
	client:send(tostring(response))
end


copas.addserver(server, clientHandler)


-- Open up socket with a clear sign
while emu.framecount() < 600 do
	gui.text(20, 20, 'Opening socket at ' .. address .. ':' .. port)
	emu.frameadvance()
end


while true do
	-- Communicate with client
	local handled, errmsg = copas.step(0)
	if handled == nil then
		print(('Socket error: %s'):format(errmsg))
	end
	
	-- Advance the game by a frame
	emu.frameadvance()
end