"""Tests for mem_pool_cli.py"""


from mem_pool_cli import (
    Buffer,
    BufferPool,
    Connection,
    ConnectionPool,
    ObjectPool,
    PoolStats,
    simulate_pool,
)


class TestPoolStats:
    def test_default(self):
        stats = PoolStats()
        assert stats.total_created == 0
        assert stats.total_acquired == 0
        assert stats.total_released == 0
        assert stats.current_in_use == 0
        assert stats.current_available == 0
        assert stats.high_water_mark == 0


class TestObjectPool:
    def test_acquire_creates_object(self):
        pool = ObjectPool(factory=lambda: {"value": 0})
        obj = pool.acquire()
        assert obj is not None
        assert obj["value"] == 0

    def test_acquire_increments_stats(self):
        pool = ObjectPool(factory=lambda: [])
        pool.acquire()
        stats = pool.stats()
        assert stats.total_created == 1
        assert stats.total_acquired == 1
        assert stats.current_in_use == 1

    def test_release_returns_to_pool(self):
        pool = ObjectPool(factory=lambda: [])
        obj = pool.acquire()
        assert pool.size() == 0
        pool.release(obj)
        assert pool.size() == 1
        stats = pool.stats()
        assert stats.total_released == 1
        assert stats.current_in_use == 0

    def test_release_resets_object(self):
        reset_called = []
        pool = ObjectPool(
            factory=lambda: {"count": 0},
            reset=lambda obj: reset_called.append(obj),
        )
        obj = pool.acquire()
        pool.release(obj)
        assert len(reset_called) == 1

    def test_reuse_pooled_object(self):
        pool = ObjectPool(factory=lambda: [])
        obj1 = pool.acquire()
        obj1_id = id(obj1)
        pool.release(obj1)

        obj2 = pool.acquire()
        assert id(obj2) == obj1_id  # Same object reused

    def test_max_size_respected(self):
        pool = ObjectPool(factory=lambda: [], max_size=2)

        objs = [pool.acquire() for _ in range(5)]
        for obj in objs:
            pool.release(obj)

        assert pool.size() <= 2

    def test_initial_size(self):
        pool = ObjectPool(factory=lambda: [], initial_size=3)
        assert pool.size() == 3
        stats = pool.stats()
        assert stats.total_created == 3

    def test_high_water_mark(self):
        pool = ObjectPool(factory=lambda: [])
        objs = [pool.acquire() for _ in range(5)]
        stats = pool.stats()
        assert stats.high_water_mark == 5

        for obj in objs[:3]:
            pool.release(obj)
        stats = pool.stats()
        assert stats.high_water_mark == 5  # Doesn't decrease

    def test_checkout_context_manager(self):
        pool = ObjectPool(factory=lambda: [], reset=lambda x: x.clear())
        with pool.checkout() as obj:
            obj.append(1)
            obj.append(2)
            assert len(obj) == 2

        # Object should be released and reset
        stats = pool.stats()
        assert stats.total_released == 1

    def test_release_unknown_object_returns_false(self):
        pool = ObjectPool(factory=lambda: [])
        unknown_obj = []
        result = pool.release(unknown_obj)
        assert result is False

    def test_clear(self):
        pool = ObjectPool(factory=lambda: [], initial_size=5)
        assert pool.size() == 5
        cleared = pool.clear()
        assert cleared == 5
        assert pool.size() == 0


class TestConnection:
    def test_create(self):
        conn = Connection(id=1)
        assert conn.id == 1
        assert conn.is_open
        assert conn.query_count == 0

    def test_execute(self):
        conn = Connection(id=1)
        result = conn.execute("SELECT 1")
        assert "conn-1" in result
        assert "SELECT 1" in result
        assert conn.query_count == 1

    def test_reset(self):
        conn = Connection(id=1)
        conn.execute("SELECT 1")
        conn.reset()
        assert conn.query_count == 0


class TestConnectionPool:
    def test_get_connection(self):
        pool = ConnectionPool(max_size=5)
        conn = pool.get_connection()
        assert conn is not None
        assert conn.id == 0

    def test_return_connection(self):
        pool = ConnectionPool(max_size=5)
        conn = pool.get_connection()
        pool.return_connection(conn)
        stats = pool.stats()
        assert stats.total_released == 1

    def test_reuses_connections(self):
        pool = ConnectionPool(max_size=5)
        conn1 = pool.get_connection()
        conn1_id = conn1.id
        pool.return_connection(conn1)

        conn2 = pool.get_connection()
        assert conn2.id == conn1_id

    def test_context_manager(self):
        pool = ConnectionPool(max_size=5)
        with pool.connection() as conn:
            conn.execute("INSERT INTO test VALUES(1)")
        stats = pool.stats()
        assert stats.total_released == 1

    def test_multiple_connections(self):
        pool = ConnectionPool(max_size=5)
        conns = [pool.get_connection() for _ in range(3)]
        assert len({c.id for c in conns}) == 3  # All different


class TestBuffer:
    def test_create(self):
        buf = Buffer()
        assert buf.position == 0
        assert buf.limit == 1024

    def test_write(self):
        buf = Buffer()
        written = buf.write(b"hello")
        assert written == 5
        assert buf.position == 5

    def test_read(self):
        buf = Buffer()
        buf.write(b"hello")
        data = buf.read(5)
        assert data == b"hello"

    def test_reset(self):
        buf = Buffer()
        buf.write(b"hello")
        buf.reset()
        assert buf.position == 0


class TestBufferPool:
    def test_acquire(self):
        pool = BufferPool(buffer_size=512)
        buf = pool.acquire()
        assert buf is not None
        assert buf.limit == 512

    def test_release(self):
        pool = BufferPool(buffer_size=512)
        buf = pool.acquire()
        buf.write(b"test")
        pool.release(buf)
        stats = pool.stats()
        assert stats.total_released == 1

    def test_context_manager(self):
        pool = BufferPool(buffer_size=512)
        with pool.buffer() as buf:
            buf.write(b"data")
        stats = pool.stats()
        assert stats.total_released == 1


class TestSimulatePool:
    def test_acquire(self):
        result = simulate_pool(["acquire:"])
        assert len(result) == 1
        assert "acquired" in result[0]

    def test_size(self):
        result = simulate_pool(["size:"])
        assert result == ["0"]

    def test_stats(self):
        result = simulate_pool(["stats:"])
        assert "created=" in result[0]

    def test_checkout(self):
        result = simulate_pool(["checkout:"])
        assert result == ["checkout complete"]


class TestPoolConcurrency:
    def test_multiple_acquires(self):
        pool = ObjectPool(factory=lambda: [], max_size=10)
        objs = [pool.acquire() for _ in range(10)]
        assert pool.in_use_count() == 10

        for obj in objs:
            pool.release(obj)
        assert pool.in_use_count() == 0


class TestPoolEdgeCases:
    def test_empty_pool_acquire(self):
        pool = ObjectPool(factory=lambda: "new")
        obj = pool.acquire()
        assert obj == "new"

    def test_release_twice(self):
        pool = ObjectPool(factory=lambda: [])
        obj = pool.acquire()
        assert pool.release(obj) is True
        assert pool.release(obj) is False  # Already released
